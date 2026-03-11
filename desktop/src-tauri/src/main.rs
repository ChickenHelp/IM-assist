//! PitWall Desktop — Tauri application entry point.
//!
//! Wraps the PitWall web frontend in a native window.
//! On macOS, provides native menu bar and window management.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running PitWall");
}
