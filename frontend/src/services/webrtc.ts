/**
 * WebRTC service for radio (audio) and screen sharing.
 *
 * Handles peer connection management, audio processing with radio effect,
 * and screen capture streaming — all over LAN (no STUN/TURN needed).
 */

type OnTrackHandler = (stream: MediaStream) => void;

export class RadioService {
  private pc: RTCPeerConnection | null = null;
  private localStream: MediaStream | null = null;
  private ws: WebSocket | null = null;
  private audioContext: AudioContext | null = null;

  /**
   * Connect to the signaling server and set up WebRTC.
   */
  async connect(signalingUrl: string, onRemoteTrack?: OnTrackHandler): Promise<void> {
    // No ICE servers needed for LAN
    this.pc = new RTCPeerConnection({ iceServers: [] });

    this.pc.ontrack = (event) => {
      onRemoteTrack?.(event.streams[0]);
    };

    // Signaling via WebSocket
    this.ws = new WebSocket(signalingUrl);

    this.ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === 'offer' && this.pc) {
        await this.pc.setRemoteDescription(new RTCSessionDescription(msg));
        const answer = await this.pc.createAnswer();
        await this.pc.setLocalDescription(answer);
        this.ws?.send(JSON.stringify(answer));
      } else if (msg.type === 'answer' && this.pc) {
        await this.pc.setRemoteDescription(new RTCSessionDescription(msg));
      } else if (msg.type === 'candidate' && this.pc) {
        await this.pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
      }
    };

    this.pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.ws?.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
      }
    };
  }

  /**
   * Start transmitting audio (push-to-talk ON).
   */
  async startTransmit(): Promise<void> {
    if (!this.pc) return;

    this.localStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    // Apply radio effect
    const processedStream = this.applyRadioEffect(this.localStream);

    processedStream.getAudioTracks().forEach((track) => {
      this.pc?.addTrack(track, processedStream);
    });
  }

  /**
   * Stop transmitting audio (push-to-talk OFF).
   */
  stopTransmit(): void {
    this.localStream?.getTracks().forEach((t) => t.stop());
    this.localStream = null;

    this.pc?.getSenders().forEach((sender) => {
      if (sender.track?.kind === 'audio') {
        this.pc?.removeTrack(sender);
      }
    });
  }

  /**
   * Apply a radio compression + static effect to the audio stream.
   */
  private applyRadioEffect(stream: MediaStream): MediaStream {
    this.audioContext = new AudioContext();
    const source = this.audioContext.createMediaStreamSource(stream);

    // Compressor — heavy compression like a radio
    const compressor = this.audioContext.createDynamicsCompressor();
    compressor.threshold.value = -30;
    compressor.knee.value = 10;
    compressor.ratio.value = 12;
    compressor.attack.value = 0.003;
    compressor.release.value = 0.1;

    // High-pass filter — remove low rumble
    const highpass = this.audioContext.createBiquadFilter();
    highpass.type = 'highpass';
    highpass.frequency.value = 300;

    // Low-pass filter — remove high frequencies (radio bandwidth)
    const lowpass = this.audioContext.createBiquadFilter();
    lowpass.type = 'lowpass';
    lowpass.frequency.value = 3500;

    // Chain: source -> highpass -> compressor -> lowpass -> destination
    source.connect(highpass);
    highpass.connect(compressor);
    compressor.connect(lowpass);

    const destination = this.audioContext.createMediaStreamDestination();
    lowpass.connect(destination);

    return destination.stream;
  }

  /**
   * Disconnect and clean up.
   */
  disconnect(): void {
    this.stopTransmit();
    this.pc?.close();
    this.ws?.close();
    this.audioContext?.close();
    this.pc = null;
    this.ws = null;
    this.audioContext = null;
  }
}

/**
 * Screen sharing service using WebRTC.
 */
export class ScreenShareService {
  private pc: RTCPeerConnection | null = null;
  private ws: WebSocket | null = null;

  /**
   * Start receiving a screen share stream.
   */
  async connectAsViewer(
    signalingUrl: string,
    onStream: (stream: MediaStream) => void,
  ): Promise<void> {
    this.pc = new RTCPeerConnection({ iceServers: [] });

    this.pc.ontrack = (event) => {
      onStream(event.streams[0]);
    };

    this.ws = new WebSocket(signalingUrl);
    this.ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'offer' && this.pc) {
        await this.pc.setRemoteDescription(new RTCSessionDescription(msg));
        const answer = await this.pc.createAnswer();
        await this.pc.setLocalDescription(answer);
        this.ws?.send(JSON.stringify(answer));
      } else if (msg.type === 'candidate' && this.pc) {
        await this.pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
      }
    };

    this.pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.ws?.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
      }
    };
  }

  /**
   * Start sharing screen (from the pilot's PC).
   */
  async startSharing(signalingUrl: string): Promise<void> {
    this.pc = new RTCPeerConnection({ iceServers: [] });

    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: { width: 1920, height: 1080, frameRate: 60 },
      audio: false,
    });

    stream.getTracks().forEach((track) => {
      this.pc?.addTrack(track, stream);
    });

    this.ws = new WebSocket(signalingUrl);

    this.ws.onopen = async () => {
      if (!this.pc) return;
      const offer = await this.pc.createOffer();
      await this.pc.setLocalDescription(offer);
      this.ws?.send(JSON.stringify(offer));
    };

    this.ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'answer' && this.pc) {
        await this.pc.setRemoteDescription(new RTCSessionDescription(msg));
      } else if (msg.type === 'candidate' && this.pc) {
        await this.pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
      }
    };

    this.pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.ws?.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
      }
    };
  }

  disconnect(): void {
    this.pc?.close();
    this.ws?.close();
    this.pc = null;
    this.ws = null;
  }
}
