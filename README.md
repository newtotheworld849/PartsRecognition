# 📐 PartsRecognition // Asset Management Prototype

Welcome to the **PartsRecognition** infrastructure archive workspace. This repository contains two structural mockups demonstrating how a modern computer vision pipeline (VLM) parses engineering assets and writes technical metadata into an immutable archival ledger.

---

## 🚀 Explore the Interactive Prototypes

Depending on your integration constraints, you can evaluate this workspace via two distinct architectural distributions:

### Option A: The Cloud-Hosted Web Application (Recommended)
This is a zero-friction distribution optimized for quick review. It renders a modern, minimalist interface complete with a real-time data table ledger and an asset image visual grid.
* **Live Deployment URL:** *[PASTE YOUR LIVE STREAMLIT WEB LINK HERE]*
* **Requirements:** None. Opens instantly in any modern web or mobile browser without downloading external interpreters.

### Option B: The Standalone Desktop Software (`desktop_app.py`)
A lightweight distribution utilizing your operating system's native window components (Tkinter). This layout demonstrates how the logic executes completely offline without external web dependencies.
* **To Execute:** Open your system command terminal and run:
  ```bash
  python desktop_app.py
  ```
* **Requirements:** Local Python 3 interpreter environment.

---

## 🛠️ Architecture & System Blueprint

Both distribution pipelines simulate a three-layer automated data sequence:
1. **Asset Ingestion Layer:** The user stages an industrial photograph or technical CAD vector diagram.
2. **Offline Inference Layer (Mock VLM):** A localized code wrapper processes the asset name and structural attributes, returning a structured data payload (Component Type, Medium, System Era, and Detailed Feature Descriptions).
3. **Storage Ledger:** Text values are safely written to an internal SQL schema (`archive.db`), and asset file streams are logged securely into an `archive_vault/` cache folder.
