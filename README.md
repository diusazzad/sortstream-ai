<div align="center">

# 🌿 SortStream AI
### Industrial Conveyor Waste Sorting & Real-Time EPA WARM v16 Carbon Accounting System

**Arbiter Hacks V1 — Devpost Hackathon Project**  
*Track: Theme Track — "Rethinking Waste"*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2F19-61DAFB.svg)](https://react.dev/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8%20%2F%20v11-FF6F00.svg)](https://ultralytics.com/)
[![ByteTrack](https://img.shields.io/badge/Object_Tracking-ByteTrack-indigo.svg)](https://github.com/ifzhang/ByteTrack)

</div>

---

## 📌 Executive Summary & Problem Statement

In standard consumer recycling apps, users snap clean photos of single objects against plain backgrounds. **In real-world Material Recovery Facilities (MRFs), the reality is chaotic:**
- Recyclables move along conveyor belts at speeds of **1.5 to 2.5 meters/second**.
- Objects are dirty, crushed, fragmented, and heavily overlapping.
- Municipal sorting lines suffer from high contamination rates, costing millions in landfill fines and incinerator penalties.

**SortStream AI** is an end-to-end industrial computer vision and lifecycle carbon accounting platform. It performs real-time continuous multi-class object detection and tracking on industrial conveyor belts, automatically calculates purity and flow rates, and mathematically quantifies diverted greenhouse gas emissions using the **U.S. EPA WARM v16 (Waste Reduction Model)** standard.

---

## 🚀 Key Features

1. **High-Speed Industrial Computer Vision:**
   - Multi-class real-time detection for recyclables: **PET (#1)**, **HDPE (#2)**, **Aluminum Cans**, **Corrugated Cardboard**, and **Hazardous/E-Waste**.
   - Built on optimized YOLO architectures for sub-30ms inference.

2. **ByteTrack Multi-Object Association (Zero Double-Counting):**
   - Implements ByteTrack Kalman-filter multi-object tracking with unique ID persistence.
   - Virtual tripwire / ROI counting boundary to ensure every waste item is counted exactly once as it traverses the sorting zone.

3. **EPA WARM v16 Dynamic Carbon & Energy Accounting:**
   - Evaluates true avoided emissions using official EPA lifecycle greenhouse gas emission factors:
     $$\Delta E_{\text{net}} = \sum_{m} M_m \times \left( EF_{\text{landfill}, m} - EF_{\text{recycle}, m} \right)$$
   - Real-time live counter for avoided $\text{kg CO}_2\text{e}$, saved energy (BTUs / kWh equivalent), and landfill volume diverted.

4. **Industrial Control Room Dashboard:**
   - Dark-mode responsive operations console (React + Tailwind CSS).
   - Live stream HUD with bounding boxes, confidence badges, velocity indicators, and tracking vectors.
   - Live telemetry: Items/minute, sorting purity percentage, contamination alarms, and exportable audit logs.

5. **Multi-Source Ingestion:**
   - Supports live RTSP/Webcam stream, local industrial conveyor MP4 simulation loop, and single-frame diagnostic inspection.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               CONVEYOR STREAM / VIDEO INPUT                 │
│         (Industrial Camera / RTSP / Video Simulation)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ Frames (OpenCV / Async Stream)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 SORTSTREAM VISION PIPELINE                  │
│  - Ultralytics YOLOv8/v11 Object Detection                  │
│  - ByteTrack Kalman Filter Association & Unique ID Tracking │
│  - Virtual Tripwire Boundary Crossing Detection             │
└──────────────────────────────┬──────────────────────────────┘
                               │ Tracked Waste Event Stream
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI CORE & EPA WARM v16 ENGINE             │
│  - Material Mass Estimator & Class Lookup                   │
│  - EPA WARM v16 Formula: Net GHG & Energy Offset Calculation│
│  - WebSockets / REST Telemetry Aggregator                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Real-Time Metrics & Video Feed
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           INDUSTRIAL REACT TELEMETRY DASHBOARD              │
│  - Live HUD Video Canvas with Bounding Boxes & Tracking IDs │
│  - Real-Time kg CO2e Avoided & Energy Savings Gauge         │
│  - Stream Throughput, Purity Ratio, & Contamination Alerts  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📐 EPA WARM v16 Mathematical Framework

SortStream AI rejects speculative carbon estimates. All emission reductions are grounded in U.S. Environmental Protection Agency (EPA) Waste Reduction Model (WARM v16) lifecycle factor differentials:

| Material Class | Avg Unit Mass (g) | Landfill Factor ($EF_L$) | Recycling Factor ($EF_R$) | Net Avoided GHG ($MTCO_2E$ / ton) |
| :--- | :---: | :---: | :---: | :---: |
| **Aluminum Cans** | 14.2 g | 0.02 | -9.13 | **9.15** |
| **PET Plastic (#1)** | 23.8 g | 0.04 | -1.16 | **1.20** |
| **HDPE Plastic (#2)** | 35.0 g | 0.04 | -0.92 | **0.96** |
| **Corrugated Cardboard** | 65.0 g | 0.23 | -3.11 | **3.34** |
| **E-Waste / Circuit** | 80.0 g | 0.05 | -1.85 | **1.90** |

*Formulas are executed per tracked boundary crossing and summed in real-time.*

---

## 📂 Project Structure

```
P:\Hackathon\devpost.com\arbiter-hacks-v1\
├── .gitignore
├── README.md
├── COMPETITION_ANALYSIS_AND_IDEAS.md
├── backend/                        # FastAPI & Computer Vision Engine
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entrypoint
│   │   ├── config.py               # Application configuration
│   │   ├── core/
│   │   │   ├── detector.py         # YOLO detection wrapper
│   │   │   ├── tracker.py          # ByteTrack multi-object tracker
│   │   │   └── pipeline.py         # Frame processing pipeline
│   │   ├── services/
│   │   │   ├── warm_calculator.py  # EPA WARM v16 emissions engine
│   │   │   └── stream_manager.py   # Video stream orchestrator
│   │   └── schemas/
│   │       ├── metrics.py          # Real-time metrics models
│   │       └── waste_event.py      # Tracked item schemas
│   ├── tests/
│   │   ├── test_warm_engine.py     # EPA WARM formula unit tests
│   │   └── test_api.py             # API route integration tests
│   ├── requirements.txt
│   └── run_server.py
├── frontend/                       # Industrial Control Dashboard
│   ├── src/
│   │   ├── components/             # Live HUD, Metrics, Carbon Counter
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── demo_assets/                    # Sample conveyor video & test traces
```

---

## 🛠️ Quick Start & Installation

### 1. Prerequisites
- **Python:** 3.11+
- **Node.js:** 18+
- **Git**

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python run_server.py
```
*Backend runs at `http://localhost:8000` (Swagger docs: `/docs`).*

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*Dashboard opens at `http://localhost:5173`.*

---

## 🏆 Devpost Arbiter Hacks V1 Alignment

| Criteria (Theme Track) | Weight | How SortStream AI Delivers |
| :--- | :---: | :--- |
| **Impact on Waste Problem** | **35%** | Directly tackles MRF sorting contamination and material recovery loss at the primary choke point: the high-speed sorting belt. Quantified via EPA WARM v16. |
| **Technical Execution** | **25%** | Production-grade pipeline uniting YOLO computer vision, ByteTrack multi-object tracking, FastAPI WebSockets, and real-time React analytics. |
| **Feasibility & Deployability** | **20%** | Compatible with standard RTSP IP cameras above sorting conveyors. Self-contained simulation mode for one-click reviewer testing. |
| **Presentation & Demo Clarity** | **20%** | Engaging, visual industrial control room UI with real-time video HUD, live carbon metrics, and audio contamination alerts. |

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
