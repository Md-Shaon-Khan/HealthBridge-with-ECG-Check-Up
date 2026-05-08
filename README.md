# 🏥 HealthBridge — Clinical Intelligence Platform

> **IoT-based ECG acquisition, AI disease prediction, and patient-doctor dashboard**  
> Arduino UNO · AD8232 · FastAPI · MongoDB Atlas · TensorFlow · ResNet1D

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HealthBridge-blue?style=for-the-badge)](https://healthbridge-shaon.netlify.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green?style=for-the-badge)](https://ecg-4ggp.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 📌 Overview

HealthBridge is a full-stack clinical intelligence platform that bridges IoT hardware with AI-powered medical analysis. It collects real ECG signals from the human body using an Arduino-based hardware module, processes and classifies them using deep learning, and presents results through a role-based web dashboard for both patients and doctors.

---

## ✨ Features

### 🫀 ECG Analysis (Hardware + AI)
- Real-time ECG acquisition via **Arduino UNO + AD8232** at **360 Hz** (MIT-BIH standard)
- SD card logging → unlimited duration `.csv` recording
- Upload `.csv` / `.txt` ECG files for AI analysis
- Automatic signal pipeline:
  - Artifact removal (flat/clipped sample interpolation)
  - Bandpass filter (0.5–45 Hz)
  - 50 Hz notch filter (power line noise)
  - Z-score normalization per segment
- **8-class arrhythmia classification** using ResNet1D
- Segment-by-segment confidence scoring
- Abnormal event clock-time detection (when recording start time is provided)

### 🤖 AI Disease Prediction
- Input: Temperature, Heart Rate, BP (Sys/Dia), Humidity, 6 symptoms
- Output: Disease class + Risk score (%) + Clinical advice
- Conditions: Heart Risk, Fever/Respiratory, Hypertension, Hypotension
- Personalized drug, diet, and routine recommendations

### 👨‍⚕️ Patient–Doctor Dashboard
- Role-based access — **Patient** and **Doctor** views
- Patient: AI Predictor, ECG Test, My Reports, Health Trend Chart, Doctor Feedback
- Doctor: Patient search, Vitals charts (Temp, BP, HR, Symptoms), ECG history, Prescription messaging
- Medical Chatbot powered by **LLaMA 3.3 70B** via Groq API

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript, Chart.js |
| Backend | FastAPI (Python 3.10+) |
| Database | MongoDB Atlas (async via Motor) |
| ML — ECG | TensorFlow/Keras — ResNet1D |
| ML — Disease | Scikit-learn (pkl model) |
| Chatbot | Groq API — LLaMA 3.3 70B Versatile |
| Hardware | Arduino UNO, AD8232, SD Card Module |
| Deployment | Netlify (frontend) · Render (backend) |

---

## 🔌 Hardware — Pin Connection

### AD8232 → Arduino UNO

| AD8232 Pin | Arduino UNO Pin | Note |
|---|---|---|
| 3.3V | 3.3V | **NOT 5V — will damage sensor** |
| GND | GND | Common ground |
| OUTPUT | A0 | Analog ECG signal |
| LO+ | D10 | Lead-off detection (+) |
| LO− | D7 | Lead-off detection (−) |
| SDN | D9 | Shutdown pin — HIGH = ON |

### SD Card Module → Arduino UNO

| SD Module Pin | Arduino UNO Pin |
|---|---|
| VCC | 5V |
| GND | GND |
| MOSI | D11 |
| MISO | D12 |
| SCK | D13 |
| CS | D4 |

### Electrode Placement (3-lead)

| Electrode | Color | Placement |
|---|---|---|
| RA | Red | Right chest |
| LA | Yellow | Left chest |
| RL | Green | Lower abdomen (reference) |

### Power
```
9V Battery → Arduino barrel jack
Arduino 3.3V regulator → AD8232 (3.3V)
SD Card Module ← Arduino 5V
```

> ⚠️ Use **9V battery** for clean signal — USB/laptop charger introduces 50 Hz noise.

---

## 📁 Project Structure

```
HealthBridge/
├── backend/
│   ├── app.py                  # FastAPI main app (V6.0)
│   ├── database.py             # MongoDB Atlas connection
│   ├── requirements.txt        # Python dependencies
│   └── model/
│       └── model_saved.pkl     # Disease prediction model (sklearn)
├── models/                     # ECG models (auto-downloaded from Google Drive)
│   └── resnet.keras
├── frontend/
│   ├── index.html              # Landing page
│   ├── dashboard.html          # Patient/Doctor dashboard
│   ├── dashboard.js            # Dashboard logic V10.0
│   └── assets/
├── ECG/
│   ├── clean_ecg.py            # Signal preprocessing
│   ├── predict_ecg.py          # Prediction script
│   └── ECG_Final_360Hz.ino    # Arduino firmware (360 Hz + SD card)
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Md-Shaon-Khan/ECG.git
cd ECG
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file:
```env
MONGO_URI=your_mongodb_atlas_connection_string
GROQ_API_KEY=your_groq_api_key
```

Run locally:
```bash
uvicorn app:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### 3. Frontend setup

Update API URL in `dashboard.js` for local testing:
```javascript
// Replace all instances of:
https://ecg-4ggp.onrender.com
// With:
http://localhost:8000
```

Open `frontend/index.html` in browser.

### 4. Arduino firmware

```
1. Open ECG/ECG_Final_360Hz.ino in Arduino IDE
2. Connect Arduino UNO via USB
3. Tools → Board → Arduino UNO
4. Tools → Port → select your COM port
5. Upload
6. Tools → Serial Plotter → 115200 baud
```

Live ECG waveform appears when electrodes are attached.
SD card saves `ecg_data.csv` automatically with no time limit.

---

## 🧠 ECG ML Pipeline

### Architecture
- **Model:** ResNet1D (auto-downloaded from Google Drive on startup)
- **Training:** MIT-BIH Arrhythmia DB · PTB-XL · CPSC 2018
- **Window:** 3600 samples = 10 seconds per segment at 360 Hz

### 8 ECG Classes

| Class | Description |
|---|---|
| Normal | Normal sinus rhythm |
| Supraventricular | SVT / PAC |
| Ventricular | VT / PVC |
| Conduction Disorder | Bundle branch block |
| Myocardial Infarction | Heart attack pattern |
| Hypertrophy | Chamber enlargement |
| Ischemia/ST-T | ST segment changes |
| Atrial Fibrillation | Irregular rhythm |

### Signal Processing Flow

```
Raw CSV upload
      ↓  parse_ecg_csv()         — extract numeric values
      ↓  ecg_clean_signal()      — interpolate flat/clipped samples
      ↓  ecg_preprocess_window() — bandpass + notch filter + Z-score
      ↓  ResNet1D.predict()      — per 10s segment
      ↓  Aggregate → top condition + confidence score
```

---

## 📊 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/api/signup` | User registration |
| POST | `/api/login` | Authentication |
| POST | `/api/predict` | Disease prediction from vitals |
| POST | `/api/ecg-predict` | ECG file upload + AI analysis |
| POST | `/api/save-ecg-report` | Save ECG report to MongoDB |
| GET | `/api/reports/{user_id}` | Get all reports for user |
| GET | `/api/search-patient` | Doctor — search patients |
| GET | `/api/doctor-stats` | Doctor dashboard statistics |
| GET | `/api/doctor-patient-list` | All patients with latest report |
| GET | `/api/patient-stats/{user_id}` | Patient disease distribution |
| POST | `/api/send-feedback` | Doctor → Patient prescription |
| GET | `/api/get-feedback/{patient_id}` | Get latest doctor feedback |
| POST | `/api/contact` | Contact form submission |
| DELETE | `/api/delete-patient/{id}` | Remove patient record |
| POST | `/api/chatbot` | Medical chatbot (LLaMA 3.3 70B) |

Full interactive docs: [https://ecg-4ggp.onrender.com/docs](https://ecg-4ggp.onrender.com/docs)

---

## 🌐 Deployment

| Component | Platform | URL |
|---|---|---|
| Frontend | Netlify | [healthbridge-shaon.netlify.app](https://healthbridge-shaon.netlify.app) |
| Backend API | Render | [ecg-4ggp.onrender.com](https://ecg-4ggp.onrender.com) |
| Database | MongoDB Atlas | Cloud hosted |
| ECG Model | Google Drive | Auto-downloaded on startup |

> **Note:** Render free tier sleeps after 15 min inactivity — first request after sleep takes ~60s.

---

## 🗃️ SD Card CSV Format

```
sample, ecg_raw, ecg_filtered
2,      530,     18
4,      521,     9
6,      489,     -23
```

Upload `ecg_data.csv` directly to HealthBridge dashboard for AI analysis.

---

## 👨‍💻 Author

**Md. Shaon Khan**  
3rd Year Undergraduate — B.Sc. in Information Technology  
Institute of Information Technology (IIT), Jahangirnagar University  
Savar, Dhaka, Bangladesh

[![GitHub](https://img.shields.io/badge/GitHub-Md--Shaon--Khan-black?style=flat&logo=github)](https://github.com/Md-Shaon-Khan)
[![Email](https://img.shields.io/badge/Email-shaon.iit52@gmail.com-red?style=flat&logo=gmail)](mailto:shaon.iit52@gmail.com)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [MIT-BIH Arrhythmia Database](https://physionet.org/content/mitdb/) — PhysioNet
- [PTB-XL ECG Dataset](https://physionet.org/content/ptb-xl/) — PhysioNet
- [CPSC 2018 ECG Challenge](http://2018.icbeb.org/Challenge.html)
- [Groq](https://groq.com) — LLaMA 3.3 70B inference
- [Analog Devices AD8232](https://www.analog.com/en/products/ad8232.html)
- [Render](https://render.com) · [Netlify](https://netlify.com) · [MongoDB Atlas](https://mongodb.com/atlas)
