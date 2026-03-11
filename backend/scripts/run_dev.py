#!/usr/bin/env python3
"""Development server launcher for PitWall backend."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8400,
        reload=True,
        log_level="info",
    )
