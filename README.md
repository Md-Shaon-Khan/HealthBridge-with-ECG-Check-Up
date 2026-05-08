# 🏥 HealthBridge — Clinical Intelligence Platform

**An Integrated IoT and AI-Based System for ECG Monitoring and Disease Prediction**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HealthBridge-blue?style=for-the-badge)](https://healthbridge-shaon.netlify.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green?style=for-the-badge)](https://ecg-4ggp.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 1. Introduction

HealthBridge is a full-stack clinical intelligence platform designed to bridge biomedical hardware with artificial intelligence-driven medical analysis. The system enables real-time electrocardiogram (ECG) acquisition, automated disease prediction, and an interactive dashboard for both patients and healthcare professionals.

The platform integrates embedded systems, signal processing, machine learning, and cloud-based deployment to deliver an end-to-end healthcare solution.

---

## 2. System Overview

HealthBridge consists of three major components:

**1. Data Acquisition Layer**
IoT-based ECG signal collection using Arduino UNO and AD8232 sensor at 360 Hz, stored via SD card module in CSV format.

**2. Processing and Intelligence Layer**
Signal preprocessing and AI-based classification using deep learning (ResNet1D) and machine learning (Scikit-learn) models.

**3. Application Layer**
Web-based dashboard for patient monitoring, doctor interaction, report visualization, and AI-powered medical chatbot.

---

## 3. Core Features

### 3.1 ECG Acquisition and Analysis

- Real-time ECG signal acquisition using **Arduino UNO + AD8232**
- Sampling rate: **360 Hz** (aligned with MIT-BIH standard)
- Continuous data logging via **SD card** in CSV format — no time limit
- Support for uploading external ECG files (`.csv`, `.txt`)

#### Signal Processing Pipeline

```
Raw Signal
    ↓  Artifact removal       — flat/clipped sample interpolation
    ↓  Bandpass filter        — 0.5 Hz to 45 Hz
    ↓  Notch filter           — 50 Hz power-line interference removal
    ↓  Z-score normalization  — per 10-second segment
    ↓  ResNet1D inference     — 8-class classification
```

#### AI Classification Output
- Per-segment prediction with confidence score
- Overall top condition with average probability
- Abnormal event clock-time detection (when recording start time is provided)

---

### 3.2 AI-Based Disease Prediction

**Input Parameters:**
- Temperature, Heart Rate, Blood Pressure (Systolic / Diastolic), Humidity
- 6 symptom features: Fever, Cough, Chest Pain, Shortness of Breath, Fatigue, Headache

**Output:**
- Predicted disease category
- Risk score (0–100%)
- Clinical recommendations (drugs, diet, routine)

**Supported Conditions:**

| Condition | Risk Levels |
|---|---|
| Cardiovascular Risk | Moderate (60–80%) / High (≥80%) |
| Hypertension | Moderate / Severe |
| Hypotension | — |
| Fever / Respiratory | Mild / Severe |

---

### 3.3 Patient–Doctor Dashboard

#### Patient Interface
- ECG file upload and AI analysis
- AI-based disease prediction form
- Historical reports with trend chart
- Doctor feedback and prescription access
- Medical chatbot for health queries

#### Doctor Interface
- Patient search and management panel
- Vital sign charts (Temperature, BP, Heart Rate, Symptoms)
- ECG report history per patient
- Prescription and feedback messaging system

---

## 4. System Architecture

### 4.1 Hardware Components

| Component | Specification |
|---|---|
| Microcontroller | Arduino UNO |
| ECG Sensor | AD8232 (3.3V supply) |
| Storage | SD Card Module (SPI) |
| Power | 9V Battery → Arduino barrel jack |
| Electrodes | 3-lead (RA, LA, RL) |

### 4.2 Pin Connection — AD8232 → Arduino UNO

| AD8232 Pin | Arduino UNO Pin | Description |
|---|---|---|
| 3.3V | 3.3V | Power — **NOT 5V** |
| GND | GND | Common ground |
| OUTPUT | A0 | Analog ECG signal |
| LO+ | D10 | Lead-off detection (+) |
| LO− | D7 | Lead-off detection (−) |
| SDN | D9 | Shutdown — HIGH = active |

### 4.3 Pin Connection — SD Card Module → Arduino UNO

| SD Module Pin | Arduino UNO Pin |
|---|---|
| VCC | 5V |
| GND | GND |
| MOSI | D11 |
| MISO | D12 |
| SCK | D13 |
| CS | D4 |

### 4.4 Software Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript, Chart.js |
| Backend | FastAPI (Python 3.10+) |
| Database | MongoDB Atlas (Motor async driver) |
| ECG Model | TensorFlow / Keras — ResNet1D |
| Disease Model | Scikit-learn (pkl) |
| Chatbot | LLaMA 3.3 70B via Groq API |
| Deployment | Netlify (frontend) · Render (backend) |

---

## 5. ECG Machine Learning Pipeline

### Model Configuration

| Parameter | Value |
|---|---|
| Architecture | ResNet1D |
| Input window | 3600 samples (10 seconds at 360 Hz) |
| Output classes | 8 |
| Training datasets | MIT-BIH · PTB-XL · CPSC 2018 |

### Classification Categories

| # | Class | Description |
|---|---|---|
| 1 | Normal | Normal sinus rhythm |
| 2 | Supraventricular | SVT / PAC |
| 3 | Ventricular | VT / PVC |
| 4 | Conduction Disorder | Bundle branch block |
| 5 | Myocardial Infarction | Heart attack ECG pattern |
| 6 | Hypertrophy | Chamber enlargement |
| 7 | Ischemia / ST-T | ST segment abnormalities |
| 8 | Atrial Fibrillation | Irregular atrial rhythm |

---

## 6. API Design

The backend exposes RESTful APIs built with FastAPI for authentication, prediction, report management, and communication.

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | System health check |
| POST | `/api/signup` | User registration |
| POST | `/api/login` | Authentication |
| POST | `/api/predict` | Disease prediction from vitals |
| POST | `/api/ecg-predict` | ECG file upload and analysis |
| POST | `/api/save-ecg-report` | Save ECG report to database |
| GET | `/api/reports/{user_id}` | Retrieve all user reports |
| GET | `/api/search-patient` | Doctor — search patients |
| GET | `/api/doctor-stats` | Doctor dashboard statistics |
| GET | `/api/doctor-patient-list` | All patients with latest report |
| GET | `/api/patient-stats/{user_id}` | Patient disease distribution |
| POST | `/api/send-feedback` | Doctor → patient prescription |
| GET | `/api/get-feedback/{patient_id}` | Retrieve latest doctor feedback |
| POST | `/api/contact` | Contact form submission |
| DELETE | `/api/delete-patient/{id}` | Remove patient record |
| POST | `/api/chatbot` | Medical chatbot (LLaMA 3.3 70B) |

Full interactive documentation: [https://ecg-4ggp.onrender.com/docs](https://ecg-4ggp.onrender.com/docs)

---

## 7. Deployment Architecture

| Component | Platform | URL |
|---|---|---|
| Frontend | Netlify | [healthbridge-shaon.netlify.app](https://healthbridge-shaon.netlify.app) |
| Backend API | Render | [ecg-4ggp.onrender.com](https://ecg-4ggp.onrender.com) |
| Database | MongoDB Atlas | Cloud hosted |
| ECG Model | Google Drive | Auto-downloaded on startup |

> **Note:** Backend may experience cold-start delay (~60s) on first request due to free-tier deployment sleep policy.

---

## 8. Data Format

### SD Card CSV Structure

```
sample, ecg_raw, ecg_filtered
2,      530,     18
4,      521,     9
6,      489,     -23
```

| Column | Description |
|---|---|
| sample | Cumulative sample number |
| ecg_raw | Raw ADC value (baseline removed) |
| ecg_filtered | Moving average filtered value |

Upload `ecg_data.csv` directly to the HealthBridge dashboard for AI analysis.

---

## 9. Implementation Workflow

```
Step 1 → ECG signal acquisition via Arduino + AD8232 hardware
Step 2 → Data stored in ecg_data.csv on SD card (360 Hz, no time limit)
Step 3 → CSV uploaded to HealthBridge web interface
Step 4 → Backend: artifact removal → bandpass → notch → Z-score
Step 5 → ResNet1D inference per 10-second segment
Step 6 → Results aggregated → top condition + confidence + segment table
Step 7 → Report saved to MongoDB Atlas → visible in My Reports
```

---

## 10. Getting Started

### Clone the repository

```bash
git clone https://github.com/Md-Shaon-Khan/ECG.git
cd ECG
```

### Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env`:
```env
MONGO_URI=your_mongodb_atlas_connection_string
GROQ_API_KEY=your_groq_api_key
```

Run locally:
```bash
uvicorn app:app --reload --port 8000
```

### Arduino firmware

```
1. Open ECG/ECG_Final_360Hz.ino in Arduino IDE
2. Connect Arduino UNO via USB
3. Tools → Board → Arduino UNO
4. Tools → Port → select COM port
5. Upload → Tools → Serial Plotter → 115200 baud
```

---

## 11. Author

**Md. Shaon Khan**
Undergraduate Student, B.Sc. in Information Technology
Institute of Information Technology (IIT), Jahangirnagar University
Savar, Dhaka, Bangladesh

[![GitHub](https://img.shields.io/badge/GitHub-Md--Shaon--Khan-black?style=flat&logo=github)](https://github.com/Md-Shaon-Khan)
[![Email](https://img.shields.io/badge/Email-shaon.iit52@gmail.com-red?style=flat&logo=gmail)](mailto:shaon.iit52@gmail.com)

---

## 12. Future Improvements

- Real-time cloud ECG streaming (no SD card dependency)
- Multi-lead ECG support (12-lead)
- Transformer-based ensemble model for improved accuracy
- Mobile application development (Flutter)
- Clinical validation with real patient datasets
- JaundiceScan module integration

---

## 13. License

MIT License — see [LICENSE](LICENSE) for details.

---

## 14. Acknowledgements

- [MIT-BIH Arrhythmia Database](https://physionet.org/content/mitdb/) — PhysioNet
- [PTB-XL ECG Dataset](https://physionet.org/content/ptb-xl/) — PhysioNet
- [CPSC 2018 ECG Challenge](http://2018.icbeb.org/Challenge.html)
- [Groq](https://groq.com) — LLaMA 3.3 70B inference API
- [Analog Devices AD8232](https://www.analog.com/en/products/ad8232.html)
- [Render](https://render.com) · [Netlify](https://netlify.com) · [MongoDB Atlas](https://mongodb.com/atlas)
