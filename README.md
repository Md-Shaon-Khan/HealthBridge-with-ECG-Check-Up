🏥 HealthBridge — Clinical Intelligence Platform

An Integrated IoT and AI-Based System for ECG Monitoring and Disease Prediction

1. Introduction

HealthBridge is a full-stack clinical intelligence platform designed to bridge biomedical hardware with artificial intelligence-driven medical analysis. The system enables real-time electrocardiogram (ECG) acquisition, automated disease prediction, and an interactive dashboard for both patients and healthcare professionals.

The platform integrates embedded systems, signal processing, machine learning, and cloud-based deployment to deliver an end-to-end healthcare solution.

2. System Overview

HealthBridge consists of three major components:

Data Acquisition Layer
IoT-based ECG signal collection using Arduino and AD8232 sensor.
Processing and Intelligence Layer
Signal preprocessing and AI-based classification using deep learning and machine learning models.
Application Layer
Web-based dashboard for patient monitoring, doctor interaction, and report visualization.
3. Core Features
3.1 ECG Acquisition and Analysis
Real-time ECG signal acquisition using Arduino UNO and AD8232 sensor
Sampling rate: 360 Hz (aligned with MIT-BIH standard)
Continuous data logging via SD card in CSV format
Support for uploading external ECG files (.csv, .txt)
Signal Processing Pipeline
Noise and artifact removal (flat/clipped signal interpolation)
Bandpass filtering (0.5–45 Hz)
Power-line interference removal using 50 Hz notch filter
Z-score normalization for each segment
AI Classification
Model: ResNet1D
Multi-class classification (8 classes)
Segment-wise prediction (10-second windows)
Confidence scoring and abnormal event detection
3.2 AI-Based Disease Prediction
Input parameters:
Temperature
Heart Rate
Blood Pressure (Systolic/Diastolic)
Humidity
Symptoms (6 features)
Output:
Predicted disease category
Risk score (%)
Clinical recommendations
Supported Conditions
Cardiovascular risk
Hypertension / Hypotension
Fever and respiratory conditions
3.3 Patient–Doctor Dashboard
Patient Interface
ECG test upload and analysis
AI-based disease prediction
Historical reports and trends
Doctor feedback access
Doctor Interface
Patient search and management
Visualization of vital signs
ECG report history
Prescription and feedback system
Additional Feature
Medical chatbot powered by LLaMA 3.3 (via Groq API)
4. System Architecture
4.1 Hardware Components
Arduino UNO
AD8232 ECG sensor
SD Card module
3-lead electrode configuration
4.2 Software Stack
Layer	Technology
Frontend	HTML5, CSS3, JavaScript, Chart.js
Backend	FastAPI (Python 3.10+)
Database	MongoDB Atlas
ECG Model	TensorFlow/Keras (ResNet1D)
Disease Model	Scikit-learn
Chatbot	LLaMA 3.3 (Groq API)
Deployment	Netlify, Render
5. ECG Machine Learning Pipeline
Model Configuration
Architecture: ResNet1D
Input window: 3600 samples (10 seconds)
Training datasets:
MIT-BIH Arrhythmia Database
PTB-XL Dataset
CPSC 2018 Dataset
Classification Categories
Normal rhythm
Supraventricular arrhythmia
Ventricular arrhythmia
Conduction disorder
Myocardial infarction
Hypertrophy
Ischemia / ST-T abnormalities
Atrial fibrillation
6. API Design

The backend exposes RESTful APIs for authentication, prediction, report management, and communication.

Key Endpoints
Method	Endpoint	Description
GET	/	System health check
POST	/api/signup	User registration
POST	/api/login	Authentication
POST	/api/predict	Disease prediction
POST	/api/ecg-predict	ECG analysis
GET	/api/reports/{user_id}	Retrieve reports
POST	/api/send-feedback	Doctor feedback
POST	/api/chatbot	AI chatbot
7. Deployment Architecture
Component	Platform
Frontend	Netlify
Backend	Render
Database	MongoDB Atlas
Model Storage	Google Drive

Note: Backend may experience cold-start delay due to free-tier deployment.

8. Data Format
ECG CSV Structure
sample, ecg_raw, ecg_filtered
2,      530,     18
4,      521,     9
6,      489,     -23
9. Implementation Workflow
ECG signal acquisition via hardware
Data storage in CSV format
Upload to web interface
Preprocessing and segmentation
Model inference (ResNet1D)
Result aggregation and visualization
10. Author

Md. Shaon Khan
Undergraduate Student, Information Technology
Institute of Information Technology (IIT)
Jahangirnagar University, Bangladesh

11. Conclusion

HealthBridge demonstrates the integration of IoT, signal processing, and artificial intelligence in modern healthcare systems. The platform provides a scalable solution for remote cardiac monitoring and preliminary disease diagnosis, enabling improved accessibility and efficiency in medical services.

12. Future Improvements
Integration of real-time cloud streaming (no SD card dependency)
Multi-lead ECG support
Advanced deep learning architectures (Transformer-based models)
Mobile application development
Clinical validation with real patient datasets