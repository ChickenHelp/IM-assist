# PitWall — Architecture Technique

## Vue d'ensemble

PitWall est une application de gestion de course en temps réel pour iRacing,
permettant à un manager/ingénieur de course de superviser un pilote depuis un
second poste connecté en réseau local (LAN).

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RÉSEAU LOCAL (LAN)                          │
│                                                                     │
│  ┌──────────────────────┐          ┌──────────────────────────────┐ │
│  │   PC PILOTE (Win)    │          │   PC MANAGER (Mac / Web)     │ │
│  │                      │          │                              │ │
│  │  ┌────────────────┐  │  WS/REST │  ┌────────────────────────┐ │ │
│  │  │    iRacing      │  │◄────────►│  │   PitWall Frontend     │ │ │
│  │  │    Simulator    │  │          │  │   (React + Tauri)      │ │ │
│  │  └───────┬─────────┘  │          │  │                        │ │ │
│  │          │ Shared Mem  │          │  │  ┌──────────────────┐  │ │ │
│  │  ┌───────▼─────────┐  │          │  │  │ Live Race Tab    │  │ │ │
│  │  │   irsdk (Python) │  │          │  │  │ Strategy Tab     │  │ │ │
│  │  │   Telemetry      │  │          │  │  │ Performance Tab  │  │ │ │
│  │  │   Collector      │  │          │  │  │ Communication    │  │ │ │
│  │  └───────┬─────────┘  │          │  │  └──────────────────┘  │ │ │
│  │          │             │          │  └────────────────────────┘ │ │
│  │  ┌───────▼─────────┐  │  WebRTC  │  ┌────────────────────────┐ │ │
│  │  │  FastAPI Server  │  │◄────────►│  │  WebRTC Audio/Video   │ │ │
│  │  │  - REST API      │  │          │  │  - Push-to-Talk       │ │ │
│  │  │  - WebSocket     │  │          │  │  - Screen Share       │ │ │
│  │  │  - WebRTC Signal │  │          │  └────────────────────────┘ │ │
│  │  │  - SQLite DB     │  │          │                              │ │
│  │  └─────────────────┘  │          └──────────────────────────────┘ │
│  └──────────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────┘
```

## Stack Technique

| Couche     | Technologie                          |
|------------|--------------------------------------|
| Simulation | iRacing + irsdk (Python)             |
| Backend    | Python 3.11+, FastAPI, WebSocket     |
| Base       | SQLite (sessions, historique)        |
| Frontend   | React 18, TypeScript, Tailwind CSS   |
| Graphiques | Recharts, Canvas API                 |
| Desktop    | Tauri 2.x (option Electron)          |
| Audio      | WebRTC (radio custom LAN)            |
| Vidéo      | WebRTC (screen share LAN)            |
| IA         | scikit-learn / règles heuristiques   |

## Flux de données

### Télémétrie (30 Hz minimum)

```
iRacing SharedMemory
    │
    ▼  irsdk.IRSDK() — lecture mémoire partagée
    │
    ▼  TelemetryCollector — normalise + horodatage
    │
    ├──► WebSocket broadcast (JSON, 30 Hz)
    │
    ├──► SQLite buffer (écriture batch 1 Hz)
    │
    └──► AI Module (analyse async)
```

### Message WebSocket type

```json
{
  "type": "telemetry",
  "timestamp": 1710000000.123,
  "session_id": "abc-123",
  "data": {
    "speed": 245.3,
    "rpm": 8500,
    "gear": 5,
    "throttle": 0.95,
    "brake": 0.0,
    "steering": -0.12,
    "fuel_level": 42.5,
    "fuel_per_lap": 2.8,
    "tyres": {
      "temp": {"fl": 95, "fr": 98, "rl": 92, "rr": 94},
      "wear": {"fl": 0.85, "fr": 0.83, "rl": 0.88, "rr": 0.87}
    },
    "lap": {"current": 15, "best": 82.345, "delta": -0.234},
    "sectors": [27.123, 28.456, 26.766],
    "position": 3,
    "interval": {"ahead": 1.234, "behind": 2.567},
    "incidents": 2,
    "conditions": {"track_temp": 38, "air_temp": 24},
    "flags": {"yellow": false, "blue": false, "black": false}
  }
}
```

## Sécurité

- Toutes les connexions sont restreintes au sous-réseau LAN
- Authentification par token JWT (session)
- WebSocket sécurisé via token dans le handshake
- Rôles : `pilot`, `manager`, `strategist`, `observer`
- Rate limiting sur l'API REST

## Modules

| Module              | Responsabilité                          |
|--------------------|-----------------------------------------|
| `telemetry`        | Collecte irsdk, normalisation, diffusion |
| `api`              | Endpoints REST (sessions, historique)    |
| `websocket`        | Diffusion temps réel                     |
| `radio`            | WebRTC signaling + audio processing      |
| `screen_share`     | WebRTC video signaling                   |
| `analysis`         | Post-course, PDF, graphiques             |
| `ai`               | Détection anomalies, suggestions         |
| `auth`             | JWT, rôles, permissions                  |
| `db`               | SQLite, migrations                       |
