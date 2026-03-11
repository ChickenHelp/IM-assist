# PitWall — iRacing Race Engineer

Real-time race management application for iRacing. A manager on a second PC
monitors telemetry, manages strategy, and communicates with the driver via
a custom radio channel — all over LAN.

```
  ┌─────────────┐     WebSocket / WebRTC     ┌─────────────────┐
  │  PC Pilote   │ ◄──────────────────────► │  PC Manager      │
  │  (Windows)   │        LAN                │  (macOS / Web)   │
  │  iRacing     │                           │  PitWall App     │
  │  + Backend   │                           │                  │
  └─────────────┘                            └─────────────────┘
```

## Quick Start

### 1. Backend (PC Pilote — Windows)

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --host 0.0.0.0 --port 8400
```

The server starts in **simulation mode** if iRacing is not running (useful
for development on macOS/Linux).

### 2. Frontend (PC Manager or any browser)

```bash
cd frontend
npm install
npm run dev
```

Open `http://<pilot-pc-ip>:5173` in the browser.

### 3. Desktop App (optional — macOS)

```bash
cd desktop
cargo tauri dev
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full technical
architecture document.

## Development Plan

See [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) for the phased
MVP development roadmap.

## Features

| Tab             | Description                                        |
|-----------------|----------------------------------------------------|
| Live Race       | Track map, standings, gauges, tyres, fuel, flags   |
| Strategy        | Pit window calculator, undercut/overcut simulation |
| Performance     | Throttle/brake traces, sector analysis, grip       |
| Communication   | WebRTC radio with push-to-talk, quick messages     |

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, WebSocket, pyirsdk, SQLite
- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts, Zustand
- **Desktop**: Tauri 2.x
- **Radio**: WebRTC with radio compression effect
- **Analysis**: PDF report generation, AI alerts module

## API

| Endpoint                          | Method | Description              |
|-----------------------------------|--------|--------------------------|
| `/ws/telemetry`                   | WS     | Live telemetry stream    |
| `/ws/radio`                       | WS     | Radio signaling          |
| `/api/v1/auth/token`              | POST   | Get session token        |
| `/api/v1/sessions`                | GET    | List sessions            |
| `/api/v1/strategy/pit-window`     | POST   | Calculate pit window     |
| `/api/v1/strategy/undercut`       | POST   | Simulate undercut        |
| `/api/v1/sessions/{id}/report`    | GET    | Download PDF report      |
| `/api/v1/health`                  | GET    | Health check             |

## License

Proprietary — All rights reserved.
