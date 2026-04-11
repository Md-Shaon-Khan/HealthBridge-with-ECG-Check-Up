# # import os
# # import sys
# # import pickle
# # import json
# # import logging
# # import httpx
# # import numpy as np
# # import pandas as pd
# # from datetime import datetime
# # from typing import Optional
# # from pathlib import Path

# # from fastapi import FastAPI, HTTPException, UploadFile, File, Form
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel, EmailStr, model_validator, root_validator
# # from dotenv import load_dotenv

# # from scipy.signal import butter, filtfilt, iirnotch
# # import tensorflow as tf
# # from tensorflow.keras import layers

# # import sys
# # from pathlib import Path
# # sys.path.append(str(Path(__file__).parent))

# # from database import (
# #     db, users_col, predictions_col, feedback_col, contact_col, init_db_indexes
# # )

# # load_dotenv()

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # app = FastAPI(title="HealthBridge API V6.0 - MongoDB Atlas")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # BASE_DIR = Path(__file__).resolve().parent
# # MODEL_PATH = BASE_DIR.parent / "model" / "model_saved.pkl"
# # ECG_MODEL_DIR = BASE_DIR.parent / "ECG Saved Model Download from Kaggle"

# # ECG_WINDOW_SIZE = 3600
# # ECG_SAMPLING_RATE = 360
# # ECG_CLASS_NAMES = [
# #     "Normal", "Supraventricular", "Ventricular",
# #     "Conduction Disorder", "Myocardial Infarction",
# #     "Hypertrophy", "Ischemia/ST-T", "Atrial Fibrillation"
# # ]
# # W_RESNET, W_INCEPTION, W_TRANSFORMER = 0.45, 0.35, 0.20

# # try:
# #     with open(MODEL_PATH, "rb") as f:
# #         package = pickle.load(f)
# #     model = package["model"]
# #     scaler = package["scaler"]
# #     label_encoder = package["label_encoder"]
# #     feature_names = package["feature_names"]
# #     numerical_cols = package["numerical_cols"]
# #     MODEL_LOADED = True
# #     logger.info("✅ Disease Prediction Model Loaded")
# # except Exception as e:
# #     MODEL_LOADED = False
# #     logger.error(f"❌ Disease model load failed: {e}")

# # @tf.keras.utils.register_keras_serializable()
# # class PositionalEncoding(layers.Layer):
# #     def __init__(self, **kwargs):
# #         super().__init__(**kwargs)

# #     def call(self, x):
# #         seq_len = tf.shape(x)[1]
# #         d_model = tf.shape(x)[2]
# #         positions = tf.range(seq_len, dtype=tf.float32)[:, tf.newaxis]
# #         dims = tf.range(d_model, dtype=tf.float32)[tf.newaxis, :]
# #         angle_rates = 1 / tf.pow(10000.0, (2 * (dims // 2)) / tf.cast(d_model, tf.float32))
# #         angles = positions * angle_rates
# #         even_mask = tf.cast(tf.math.floormod(dims, 2) == 0, tf.float32)
# #         odd_mask = 1 - even_mask
# #         angles = tf.sin(angles) * even_mask + tf.cos(angles) * odd_mask
# #         return x + angles[tf.newaxis, :, :]

# #     def get_config(self):
# #         return super().get_config()

# # _ecg_models = None

# # def get_ecg_models():
# #     global _ecg_models
# #     if _ecg_models is not None:
# #         return _ecg_models

# #     model_files = {
# #         "resnet": "resnet_final.keras",
# #         "inception": "inception_final.keras",
# #         "transformer": "transformer_final.keras",
# #     }
# #     custom_objects = {'PositionalEncoding': PositionalEncoding}
# #     loaded = {}
# #     for name, fname in model_files.items():
# #         path = ECG_MODEL_DIR / fname
# #         if not path.exists():
# #             raise HTTPException(status_code=503, detail=f"ECG model '{fname}' not found.")
# #         logger.info(f"Loading ECG model: {name}...")
# #         loaded[name] = tf.keras.models.load_model(str(path), custom_objects=custom_objects)
# #     _ecg_models = loaded
# #     logger.info("✅ All ECG Models Loaded")
# #     return _ecg_models

# # class ContactMessage(BaseModel):
# #     full_name: str
# #     medical_id: Optional[str] = None
# #     email: Optional[EmailStr] = None
# #     phone: Optional[str] = None
# #     subject: Optional[str] = None
# #     message: Optional[str] = None

# #     @model_validator(mode='after')
# #     def validate_communication_method(self):
# #         if not self.email and not self.phone:
# #             raise ValueError('Either Email or Phone is required.')
# #         return self

# # class UserSignup(BaseModel):
# #     user_id: str
# #     name: str
# #     email: Optional[str] = None
# #     phone: Optional[str] = None
# #     role: str
# #     password: str
# #     dept: Optional[str] = None
# #     blood_group: Optional[str] = None

# #     @root_validator(pre=True)
# #     def check_contact_info(cls, values):
# #         if not values.get('email') and not values.get('phone'):
# #             raise ValueError('Either email or phone must be provided')
# #         return values

# # class HealthInput(BaseModel):
# #     user_id: str
# #     temperature: float
# #     heart_rate: float
# #     bp_dia: float
# #     bp_sys: float
# #     humidity: float
# #     fever: int
# #     cough: int
# #     chest_pain: int
# #     shortness_breath: int
# #     fatigue: int
# #     headache: int

# # class ChatbotRequest(BaseModel):
# #     user_id: str
# #     message: str

# # class SaveEcgReportRequest(BaseModel):
# #     user_id: str
# #     report_type: str = "ecg"
# #     result_status: str
# #     analysis_score: float
# #     ecg_filename: Optional[str] = None
# #     ecg_meta: Optional[str] = None
# #     suggested_drugs: Optional[str] = ""
# #     suggested_foods: Optional[str] = ""
# #     routine: Optional[str] = ""

# # def get_clinical_advice(disease, score):
# #     advice = {"drugs": "Consult Doctor", "foods": "Balanced Diet", "routine": "Rest"}
# #     if disease == "Heart_Risk":
# #         if 60 <= score < 80:
# #             advice = {
# #                 "drugs": "Aspirin (75mg) - 1 tab after lunch; Atorvastatin (10mg) - 1 tab at night",
# #                 "foods": "Walnuts, Oats, Garlic, Low-sodium meals",
# #                 "routine": "Avoid heavy lifting, 15 min slow walk"
# #             }
# #         elif score >= 80:
# #             advice = {
# #                 "drugs": "Nitroglycerin (emergency); Clopidogrel (75mg) - 1 tab daily",
# #                 "foods": "Strict heart-healthy diet, Fatty fish, Zero added salt",
# #                 "routine": "Immediate cardiology consultation. Complete bed rest"
# #             }
# #     elif disease == "Fever_Respiratory":
# #         if score < 80:
# #             advice = {
# #                 "drugs": "Paracetamol (500mg) - 1 tab after meals (max 3/day)",
# #                 "foods": "Warm soup, Citrus fruits, Ginger tea",
# #                 "routine": "Steam inhalation twice daily"
# #             }
# #         else:
# #             advice = {
# #                 "drugs": "Paracetamol (650mg) - every 6h; Azithromycin (500mg) - 1 tab daily",
# #                 "foods": "High-protein soft diet, ORS, Honey-lemon water",
# #                 "routine": "Strict isolation. Monitor SpO2 levels"
# #             }
# #     elif disease == "Hypertension":
# #         if 60 <= score < 80:
# #             advice = {
# #                 "drugs": "Amlodipine (5mg) - 1 tab morning",
# #                 "foods": "Bananas, Spinach, Skim milk. Avoid raw salt",
# #                 "routine": "30 mins brisk walking. No nicotine"
# #             }
# #         else:
# #             advice = {
# #                 "drugs": "Losartan (50mg) daily; Hydrochlorothiazide (12.5mg) morning",
# #                 "foods": "Beetroot juice, Pomegranate. Zero added salt",
# #                 "routine": "Stress management (Yoga). Regular BP monitoring"
# #             }
# #     elif disease == "Hypotension":
# #         advice = {
# #             "drugs": "ORS (1L throughout day); Vitamin B12 supplements",
# #             "foods": "Cheese, Olives, Salty snacks (moderate), Coffee",
# #             "routine": "Elevate legs while resting. Avoid sudden movements"
# #         }
# #     return advice

# # def ecg_preprocess_window(signal: np.ndarray, fs: int = ECG_SAMPLING_RATE) -> np.ndarray:
# #     nyq = 0.5 * fs
# #     low = 0.5 / nyq
# #     high = min(45.0 / nyq, 0.99)
# #     b, a = butter(3, [low, high], btype='bandpass')
# #     sig = filtfilt(b, a, signal)
# #     w0 = 50.0 / nyq
# #     if w0 < 1.0:
# #         bn, an = iirnotch(w0, 30)
# #         sig = filtfilt(bn, an, sig)
# #     mean = np.mean(sig)
# #     std = np.std(sig)
# #     return ((sig - mean) / (std + 1e-8)).astype(np.float32)

# # def ecg_clean_signal(signal: np.ndarray) -> np.ndarray:
# #     bad_mask = np.abs(signal - 512) <= 5
# #     bad_mask |= (signal <= 2) | (signal >= 1021)
# #     if np.any(bad_mask):
# #         indices = np.arange(len(signal))
# #         good_idx = indices[~bad_mask]
# #         good_val = signal[~bad_mask]
# #         if len(good_val) >= 2:
# #             signal[bad_mask] = np.interp(indices[bad_mask], good_idx, good_val)
# #     return signal

# # def parse_ecg_csv(content: str) -> Optional[np.ndarray]:
# #     try:
# #         lines = content.replace(',', ' ').replace('\t', ' ').strip().splitlines()
# #         values = []
# #         for line in lines:
# #             line = line.strip()
# #             if not line or line.startswith('#'):
# #                 continue
# #             for tok in line.split():
# #                 try:
# #                     v = float(tok)
# #                     if np.isfinite(v):
# #                         values.append(v)
# #                 except ValueError:
# #                     continue
# #         if not values:
# #             return None
# #         return np.array(values, dtype=np.float64)
# #     except Exception:
# #         return None

# # def ecg_predict_signal(signal: np.ndarray, models: dict) -> dict:
# #     total_samples = len(signal)
# #     n_segments = int(total_samples // ECG_WINDOW_SIZE)
# #     if n_segments == 0:
# #         raise HTTPException(status_code=400, detail=f"Signal too short. Need ≥ {ECG_WINDOW_SIZE} samples.")
# #     all_class_probs = np.zeros(len(ECG_CLASS_NAMES))
# #     segments_result = []
# #     for seg_idx in range(n_segments):
# #         start = seg_idx * ECG_WINDOW_SIZE
# #         end = start + ECG_WINDOW_SIZE
# #         start_sec = round(start / ECG_SAMPLING_RATE, 1)
# #         end_sec = round(end / ECG_SAMPLING_RATE, 1)
# #         window = signal[start:end].copy()
# #         window = ecg_preprocess_window(window)
# #         x = window.reshape(1, ECG_WINDOW_SIZE, 1).astype(np.float32)
# #         p_r = models["resnet"].predict(x, verbose=0)[0]
# #         p_i = models["inception"].predict(x, verbose=0)[0]
# #         p_t = models["transformer"].predict(x, verbose=0)[0]
# #         ensemble = W_RESNET * p_r + W_INCEPTION * p_i + W_TRANSFORMER * p_t
# #         class_idx = int(np.argmax(ensemble))
# #         confidence = float(ensemble[class_idx])
# #         all_class_probs += ensemble
# #         segments_result.append({
# #             "seg": seg_idx + 1,
# #             "start_t": start_sec,
# #             "end_t": end_sec,
# #             "prediction": ECG_CLASS_NAMES[class_idx],
# #             "confidence": round(confidence, 4),
# #         })
# #     avg_probs = all_class_probs / n_segments
# #     top_idx = int(np.argmax(avg_probs))
# #     top_condition = ECG_CLASS_NAMES[top_idx]
# #     top_prob = float(avg_probs[top_idx]) * 100
# #     normal_count = sum(1 for s in segments_result if s["prediction"] == "Normal")
# #     return {
# #         "top_condition": top_condition,
# #         "top_prob": round(top_prob, 2),
# #         "normal_count": normal_count,
# #         "abnormal_count": n_segments - normal_count,
# #         "total_segments": n_segments,
# #         "class_probs": {
# #             ECG_CLASS_NAMES[i]: round(float(avg_probs[i]) * 100, 2)
# #             for i in range(len(ECG_CLASS_NAMES))
# #         },
# #         "segments": segments_result,
# #     }

# # @app.on_event("startup")
# # async def startup_event():
# #     await init_db_indexes()
# #     logger.info("✅ MongoDB indexes created")

# # @app.post("/api/signup")
# # async def signup(user: UserSignup):
# #     existing = await users_col.find_one({"user_id": user.user_id})
# #     if existing:
# #         raise HTTPException(status_code=400, detail="User ID already registered.")
# #     user_doc = user.dict()
# #     user_doc["password_hash"] = user_doc.pop("password")
# #     user_doc["created_at"] = datetime.utcnow()
# #     await users_col.insert_one(user_doc)
# #     return {"status": "success", "message": "Account created successfully"}

# # @app.post("/api/login")
# # async def login(data: dict):
# #     user = await users_col.find_one({
# #         "user_id": data['user_id'],
# #         "password_hash": data['password']
# #     })
# #     if not user:
# #         raise HTTPException(status_code=401, detail="Invalid credentials")
# #     return {
# #         "user_id": user['user_id'],
# #         "name": user['name'],
# #         "role": user['role']
# #     }

# # @app.post("/api/predict")
# # async def predict(input_data: HealthInput):
# #     raw_features = [
# #         input_data.temperature, input_data.heart_rate, input_data.bp_sys,
# #         input_data.bp_dia, input_data.humidity, input_data.fever,
# #         input_data.cough, input_data.chest_pain, input_data.shortness_breath,
# #         input_data.fatigue, input_data.headache
# #     ]
# #     df = pd.DataFrame([raw_features], columns=feature_names)
# #     df[numerical_cols] = scaler.transform(df[numerical_cols])
# #     proba = model.predict(df.values, verbose=0)
# #     disease = label_encoder.inverse_transform([np.argmax(proba)])[0]
# #     score = round(float(np.max(proba)) * 100, 2)
# #     advice = get_clinical_advice(disease, score)

# #     pred_doc = {
# #         "user_id": input_data.user_id,
# #         "service_type": "AI Checkup",
# #         "result_status": disease,
# #         "analysis_score": score,
# #         "temperature": input_data.temperature,
# #         "heart_rate": input_data.heart_rate,
# #         "bp_sys": input_data.bp_sys,
# #         "bp_dia": input_data.bp_dia,
# #         "humidity": input_data.humidity,
# #         "fever": input_data.fever,
# #         "cough": input_data.cough,
# #         "chest_pain": input_data.chest_pain,
# #         "shortness_breath": input_data.shortness_breath,
# #         "fatigue": input_data.fatigue,
# #         "headache": input_data.headache,
# #         "suggested_drugs": advice['drugs'],
# #         "suggested_foods": advice['foods'],
# #         "clinical_routine": advice['routine'],
# #         "created_at": datetime.utcnow()
# #     }
# #     await predictions_col.insert_one(pred_doc)
# #     return {"prediction": disease, "score": score, **advice}

# # @app.post("/api/ecg-predict")
# # async def ecg_predict(
# #     file: UploadFile = File(...),
# #     user_id: str = Form(...),
# #     start_time: Optional[str] = Form(None)
# # ):
# #     filename = file.filename or ""
# #     ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
# #     if ext not in ('csv', 'txt'):
# #         raise HTTPException(status_code=400, detail="Only .csv and .txt files supported.")
# #     content_bytes = await file.read()
# #     try:
# #         content = content_bytes.decode('utf-8', errors='ignore')
# #     except Exception:
# #         raise HTTPException(status_code=400, detail="Cannot decode file.")
# #     signal = parse_ecg_csv(content)
# #     if signal is None or len(signal) == 0:
# #         raise HTTPException(status_code=400, detail="No numeric values found.")
# #     if len(signal) < ECG_WINDOW_SIZE:
# #         raise HTTPException(status_code=400, detail=f"Signal too short. Need ≥ {ECG_WINDOW_SIZE} samples.")
# #     signal = ecg_clean_signal(signal)
# #     try:
# #         models = get_ecg_models()
# #     except Exception as e:
# #         logger.error(f"ECG model load error: {e}")
# #         raise HTTPException(status_code=503, detail="ECG model unavailable")
# #     try:
# #         result = ecg_predict_signal(signal, models)
# #     except Exception as e:
# #         logger.error(f"ECG prediction error: {e}")
# #         raise HTTPException(status_code=500, detail="Prediction failed")
# #     return result

# # @app.post("/api/save-ecg-report")
# # async def save_ecg_report(data: SaveEcgReportRequest):
# #     user = await users_col.find_one({"user_id": data.user_id})
# #     if not user:
# #         raise HTTPException(status_code=404, detail="User not found")
# #     report_doc = {
# #         "user_id": data.user_id,
# #         "service_type": "ECG Test",
# #         "report_type": data.report_type,
# #         "result_status": data.result_status,
# #         "analysis_score": float(data.analysis_score),
# #         "ecg_filename": data.ecg_filename,
# #         "ecg_meta": data.ecg_meta,
# #         "suggested_drugs": data.suggested_drugs or "",
# #         "suggested_foods": data.suggested_foods or "",
# #         "clinical_routine": data.routine or "",
# #         "created_at": datetime.utcnow()
# #     }
# #     await predictions_col.insert_one(report_doc)
# #     return {"status": "success", "message": "ECG report saved."}

# # @app.get("/api/reports/{user_id}")
# # async def get_reports(user_id: str):
# #     cursor = predictions_col.find({"user_id": user_id}).sort("created_at", -1)
# #     reports = await cursor.to_list(length=100)
# #     for r in reports:
# #         r["_id"] = str(r["_id"])
# #         if "created_at" in r:
# #             r["created_at"] = r["created_at"].isoformat()
# #     return reports

# # @app.get("/api/search-patient")
# # async def search_patient(q: str = ""):
# #     query = {"role": "patient"}
# #     if q:
# #         query["$or"] = [
# #             {"name": {"$regex": q, "$options": "i"}},
# #             {"user_id": {"$regex": q, "$options": "i"}}
# #         ]
# #     cursor = users_col.find(query, {"user_id": 1, "name": 1, "role": 1, "_id": 0})
# #     patients = await cursor.to_list(length=100)
# #     return [{"id_str": p["user_id"], "user_id": p["user_id"], "name": p["name"]} for p in patients]

# # @app.delete("/api/delete-patient/{patient_id}")
# # async def delete_patient(patient_id: str):
# #     await predictions_col.delete_many({"user_id": patient_id})
# #     await feedback_col.delete_many({"patient_id": patient_id})
# #     await users_col.delete_one({"user_id": patient_id})
# #     return {"status": "success"}

# # @app.post("/api/send-feedback")
# # async def send_feedback(data: dict):
# #     fb_doc = {
# #         "doctor_id": data['doctor_id'],
# #         "patient_id": data['patient_id'],
# #         "message": data['message'],
# #         "prescribed_at": datetime.utcnow()
# #     }
# #     await feedback_col.insert_one(fb_doc)
# #     return {"status": "success"}

# # @app.get("/api/get-feedback/{patient_id}")
# # async def get_feedback(patient_id: str):
# #     fb = await feedback_col.find_one(
# #         {"patient_id": patient_id},
# #         sort=[("prescribed_at", -1)]
# #     )
# #     if fb:
# #         return {"message": fb["message"]}
# #     return {"message": "No clinical instructions deployed yet."}

# # @app.post("/api/contact")
# # async def save_contact_message(contact: ContactMessage):
# #     await contact_col.insert_one(contact.dict())
# #     return {"status": "success", "message": "Inquiry transmitted successfully."}

# # @app.get("/api/doctor-stats")
# # async def get_doctor_stats():
# #     total_patients = await users_col.count_documents({"role": "patient"})
# #     total_checks = await predictions_col.count_documents({})
# #     responded = len(await feedback_col.distinct("patient_id"))
# #     return {
# #         "total_patients": total_patients,
# #         "total_checks": total_checks,
# #         "responded": responded,
# #         "pending": total_patients - responded
# #     }

# # @app.get("/api/doctor-patient-list")
# # async def get_doctor_patient_list():
# #     patients = await users_col.find({"role": "patient"}, {"user_id": 1, "name": 1}).to_list(length=1000)
# #     result = []
# #     for p in patients:
# #         latest = await predictions_col.find_one(
# #             {"user_id": p["user_id"]},
# #             sort=[("created_at", -1)]
# #         )
# #         if latest:
# #             result.append({
# #                 "id_str": p["user_id"],
# #                 "name": p["name"],
# #                 "latest_disease": latest.get("result_status", ""),
# #                 "latest_risk": latest.get("analysis_score"),
# #                 "latest_date": latest["created_at"].isoformat() if latest.get("created_at") else None
# #             })
# #         else:
# #             result.append({
# #                 "id_str": p["user_id"],
# #                 "name": p["name"],
# #                 "latest_disease": "No checkup yet",
# #                 "latest_risk": None,
# #                 "latest_date": None
# #             })
# #     return result

# # @app.get("/api/patient-stats/{user_id}")
# # async def get_patient_stats(user_id: str):
# #     pipeline = [
# #         {"$match": {"user_id": user_id}},
# #         {"$group": {"_id": "$result_status", "count": {"$sum": 1}}},
# #         {"$sort": {"count": -1}}
# #     ]
# #     stats = await predictions_col.aggregate(pipeline).to_list(length=20)
# #     total = await predictions_col.count_documents({"user_id": user_id})
# #     disease_dist = [{"disease": s["_id"], "count": s["count"]} for s in stats]
# #     return {"total_visits": total, "disease_distribution": disease_dist}

# # @app.post("/api/chatbot")
# # async def chatbot(request: ChatbotRequest):
# #     user = await users_col.find_one({"user_id": request.user_id})
# #     if not user:
# #         raise HTTPException(status_code=404, detail="User not found")

# #     reports = await predictions_col.find({"user_id": request.user_id}).sort("created_at", -1).to_list(length=10)

# #     if reports:
# #         lines = ["Patient's medical history (most recent first):"]
# #         for r in reports:
# #             date_str = r['created_at'].strftime("%Y-%m-%d %H:%M") if r.get('created_at') else "Unknown"
# #             lines.append(
# #                 f"- {date_str}: {r.get('result_status','')} (Risk: {r.get('analysis_score','')}%) | "
# #                 f"Drugs: {r.get('suggested_drugs','')} | Foods: {r.get('suggested_foods','')} | Routine: {r.get('clinical_routine','')}"
# #             )
# #         context = "\n".join(lines)
# #     else:
# #         context = "No previous medical reports available."

# #     prompt = f"You are a helpful medical assistant. Based on the following patient history, answer the user's question.\n\n{context}\n\nUser question: {request.message}\n\nProvide a concise, informative answer."

# #     groq_api_key = os.getenv("GROQ_API_KEY")
# #     if not groq_api_key:
# #         raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment")
# #     async with httpx.AsyncClient() as client:
# #         response = await client.post(
# #             "https://api.groq.com/openai/v1/chat/completions",
# #             json={
# #                 "model": "llama-3.3-70b-versatile",
# #                 "messages": [
# #                     {"role": "system", "content": "You are a helpful medical assistant."},
# #                     {"role": "user", "content": prompt}
# #                 ],
# #                 "temperature": 0.2,
# #                 "max_tokens": 500
# #             },
# #             headers={"Authorization": f"Bearer {groq_api_key}"}
# #         )
# #         if response.status_code == 429:
# #             return {"reply": "High demand. Please try again later."}
# #         if response.status_code != 200:
# #             raise HTTPException(status_code=502, detail="AI service unavailable")
# #         data = response.json()
# #         reply = data['choices'][0]['message']['content']
# #     return {"reply": reply}

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="127.0.0.1", port=8000)

# import os
# import sys
# import pickle
# import json
# import logging
# import httpx
# import numpy as np
# import pandas as pd
# import gdown
# from datetime import datetime
# from typing import Optional
# from pathlib import Path

# from fastapi import FastAPI, HTTPException, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr, model_validator, root_validator
# from dotenv import load_dotenv

# from scipy.signal import butter, filtfilt, iirnotch
# import tensorflow as tf
# from tensorflow.keras import layers

# sys.path.append(str(Path(__file__).parent))

# from database import (
#     db, users_col, predictions_col, feedback_col, contact_col, init_db_indexes
# )

# load_dotenv()

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(title="HealthBridge API V6.0 - MongoDB Atlas")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# BASE_DIR = Path(__file__).resolve().parent

# # ✅ FIX 1: MODEL_PATH now inside repo → backend/model/model_saved.pkl
# MODEL_PATH = BASE_DIR / "model" / "model_saved.pkl"

# # ✅ ECG models download folder (auto-created)
# ECG_MODEL_DIR = BASE_DIR / "models"
# ECG_MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ECG_WINDOW_SIZE  = 3600
# ECG_SAMPLING_RATE = 360
# ECG_CLASS_NAMES  = [
#     "Normal", "Supraventricular", "Ventricular",
#     "Conduction Disorder", "Myocardial Infarction",
#     "Hypertrophy", "Ischemia/ST-T", "Atrial Fibrillation"
# ]
# W_RESNET, W_INCEPTION, W_TRANSFORMER = 0.45, 0.35, 0.20

# # ── Disease prediction model ──────────────────────────────────────────────────
# try:
#     with open(MODEL_PATH, "rb") as f:
#         package = pickle.load(f)
#     model         = package["model"]
#     scaler        = package["scaler"]
#     label_encoder = package["label_encoder"]
#     feature_names = package["feature_names"]
#     numerical_cols = package["numerical_cols"]
#     MODEL_LOADED  = True
#     logger.info("✅ Disease Prediction Model Loaded")
# except Exception as e:
#     MODEL_LOADED  = False
#     logger.error(f"❌ Disease model load failed: {e}")


# # ── Custom Keras layer ────────────────────────────────────────────────────────
# @tf.keras.utils.register_keras_serializable()
# class PositionalEncoding(layers.Layer):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def call(self, x):
#         seq_len     = tf.shape(x)[1]
#         d_model     = tf.shape(x)[2]
#         positions   = tf.range(seq_len, dtype=tf.float32)[:, tf.newaxis]
#         dims        = tf.range(d_model,  dtype=tf.float32)[tf.newaxis, :]
#         angle_rates = 1 / tf.pow(10000.0, (2 * (dims // 2)) / tf.cast(d_model, tf.float32))
#         angles      = positions * angle_rates
#         even_mask   = tf.cast(tf.math.floormod(dims, 2) == 0, tf.float32)
#         odd_mask    = 1 - even_mask
#         angles      = tf.sin(angles) * even_mask + tf.cos(angles) * odd_mask
#         return x + angles[tf.newaxis, :, :]

#     def get_config(self):
#         return super().get_config()


# # ── Google Drive downloader ───────────────────────────────────────────────────
# def download_model(file_id: str, filename: str):
#     """Download model from Google Drive if not cached, then load it."""
#     path = ECG_MODEL_DIR / filename
#     if not path.exists():
#         logger.info(f"⬇️  Downloading {filename} from Google Drive …")
#         gdown.download(f"https://drive.google.com/uc?id={file_id}", str(path), quiet=False)
#         logger.info(f"✅ Downloaded: {filename}")
#     else:
#         logger.info(f"✅ Cached model found: {filename}")
#     return tf.keras.models.load_model(
#         str(path),
#         custom_objects={"PositionalEncoding": PositionalEncoding}
#     )


# # ── Global ECG model references ───────────────────────────────────────────────
# resnet_model      = None
# inception_model   = None
# transformer_model = None


# def get_ecg_models() -> dict:
#     if resnet_model is None or inception_model is None or transformer_model is None:
#         raise HTTPException(
#             status_code=503,
#             detail="ECG models not loaded yet. Please retry in a moment."
#         )
#     return {
#         "resnet":      resnet_model,
#         "inception":   inception_model,
#         "transformer": transformer_model,
#     }


# # ── Pydantic schemas ──────────────────────────────────────────────────────────
# class ContactMessage(BaseModel):
#     full_name:  str
#     medical_id: Optional[str]      = None
#     email:      Optional[EmailStr] = None
#     phone:      Optional[str]      = None
#     subject:    Optional[str]      = None
#     message:    Optional[str]      = None

#     @model_validator(mode='after')
#     def validate_communication_method(self):
#         if not self.email and not self.phone:
#             raise ValueError('Either Email or Phone is required.')
#         return self


# class UserSignup(BaseModel):
#     user_id:     str
#     name:        str
#     email:       Optional[str] = None
#     phone:       Optional[str] = None
#     role:        str
#     password:    str
#     dept:        Optional[str] = None
#     blood_group: Optional[str] = None

#     @root_validator(pre=True)
#     def check_contact_info(cls, values):
#         if not values.get('email') and not values.get('phone'):
#             raise ValueError('Either email or phone must be provided')
#         return values


# class HealthInput(BaseModel):
#     user_id:          str
#     temperature:      float
#     heart_rate:       float
#     bp_dia:           float
#     bp_sys:           float
#     humidity:         float
#     fever:            int
#     cough:            int
#     chest_pain:       int
#     shortness_breath: int
#     fatigue:          int
#     headache:         int


# class ChatbotRequest(BaseModel):
#     user_id: str
#     message: str


# class SaveEcgReportRequest(BaseModel):
#     user_id:         str
#     report_type:     str           = "ecg"
#     result_status:   str
#     analysis_score:  float
#     ecg_filename:    Optional[str] = None
#     ecg_meta:        Optional[str] = None
#     suggested_drugs: Optional[str] = ""
#     suggested_foods: Optional[str] = ""
#     routine:         Optional[str] = ""


# # ── Clinical advice helper ────────────────────────────────────────────────────
# def get_clinical_advice(disease: str, score: float) -> dict:
#     advice = {"drugs": "Consult Doctor", "foods": "Balanced Diet", "routine": "Rest"}
#     if disease == "Heart_Risk":
#         if 60 <= score < 80:
#             advice = {
#                 "drugs":   "Aspirin (75mg) - 1 tab after lunch; Atorvastatin (10mg) - 1 tab at night",
#                 "foods":   "Walnuts, Oats, Garlic, Low-sodium meals",
#                 "routine": "Avoid heavy lifting, 15 min slow walk"
#             }
#         elif score >= 80:
#             advice = {
#                 "drugs":   "Nitroglycerin (emergency); Clopidogrel (75mg) - 1 tab daily",
#                 "foods":   "Strict heart-healthy diet, Fatty fish, Zero added salt",
#                 "routine": "Immediate cardiology consultation. Complete bed rest"
#             }
#     elif disease == "Fever_Respiratory":
#         if score < 80:
#             advice = {
#                 "drugs":   "Paracetamol (500mg) - 1 tab after meals (max 3/day)",
#                 "foods":   "Warm soup, Citrus fruits, Ginger tea",
#                 "routine": "Steam inhalation twice daily"
#             }
#         else:
#             advice = {
#                 "drugs":   "Paracetamol (650mg) - every 6h; Azithromycin (500mg) - 1 tab daily",
#                 "foods":   "High-protein soft diet, ORS, Honey-lemon water",
#                 "routine": "Strict isolation. Monitor SpO2 levels"
#             }
#     elif disease == "Hypertension":
#         if 60 <= score < 80:
#             advice = {
#                 "drugs":   "Amlodipine (5mg) - 1 tab morning",
#                 "foods":   "Bananas, Spinach, Skim milk. Avoid raw salt",
#                 "routine": "30 mins brisk walking. No nicotine"
#             }
#         else:
#             advice = {
#                 "drugs":   "Losartan (50mg) daily; Hydrochlorothiazide (12.5mg) morning",
#                 "foods":   "Beetroot juice, Pomegranate. Zero added salt",
#                 "routine": "Stress management (Yoga). Regular BP monitoring"
#             }
#     elif disease == "Hypotension":
#         advice = {
#             "drugs":   "ORS (1L throughout day); Vitamin B12 supplements",
#             "foods":   "Cheese, Olives, Salty snacks (moderate), Coffee",
#             "routine": "Elevate legs while resting. Avoid sudden movements"
#         }
#     return advice


# # ── ECG signal helpers ────────────────────────────────────────────────────────
# def ecg_preprocess_window(signal: np.ndarray, fs: int = ECG_SAMPLING_RATE) -> np.ndarray:
#     nyq  = 0.5 * fs
#     low  = 0.5 / nyq
#     high = min(45.0 / nyq, 0.99)
#     b, a = butter(3, [low, high], btype='bandpass')
#     sig  = filtfilt(b, a, signal)
#     w0   = 50.0 / nyq
#     if w0 < 1.0:
#         bn, an = iirnotch(w0, 30)
#         sig = filtfilt(bn, an, sig)
#     mean = np.mean(sig)
#     std  = np.std(sig)
#     return ((sig - mean) / (std + 1e-8)).astype(np.float32)


# def ecg_clean_signal(signal: np.ndarray) -> np.ndarray:
#     bad_mask  = np.abs(signal - 512) <= 5
#     bad_mask |= (signal <= 2) | (signal >= 1021)
#     if np.any(bad_mask):
#         indices  = np.arange(len(signal))
#         good_idx = indices[~bad_mask]
#         good_val = signal[~bad_mask]
#         if len(good_val) >= 2:
#             signal[bad_mask] = np.interp(indices[bad_mask], good_idx, good_val)
#     return signal


# def parse_ecg_csv(content: str) -> Optional[np.ndarray]:
#     try:
#         lines  = content.replace(',', ' ').replace('\t', ' ').strip().splitlines()
#         values = []
#         for line in lines:
#             line = line.strip()
#             if not line or line.startswith('#'):
#                 continue
#             for tok in line.split():
#                 try:
#                     v = float(tok)
#                     if np.isfinite(v):
#                         values.append(v)
#                 except ValueError:
#                     continue
#         return np.array(values, dtype=np.float64) if values else None
#     except Exception:
#         return None


# def ecg_predict_signal(signal: np.ndarray, models: dict) -> dict:
#     n_segments = int(len(signal) // ECG_WINDOW_SIZE)
#     if n_segments == 0:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Signal too short. Need ≥ {ECG_WINDOW_SIZE} samples."
#         )
#     all_class_probs = np.zeros(len(ECG_CLASS_NAMES))
#     segments_result = []
#     for seg_idx in range(n_segments):
#         start     = seg_idx * ECG_WINDOW_SIZE
#         end       = start + ECG_WINDOW_SIZE
#         start_sec = round(start / ECG_SAMPLING_RATE, 1)
#         end_sec   = round(end   / ECG_SAMPLING_RATE, 1)
#         window    = ecg_preprocess_window(signal[start:end].copy())
#         x         = window.reshape(1, ECG_WINDOW_SIZE, 1).astype(np.float32)
#         p_r = models["resnet"].predict(x,      verbose=0)[0]
#         p_i = models["inception"].predict(x,   verbose=0)[0]
#         p_t = models["transformer"].predict(x, verbose=0)[0]
#         ensemble  = W_RESNET * p_r + W_INCEPTION * p_i + W_TRANSFORMER * p_t
#         class_idx = int(np.argmax(ensemble))
#         all_class_probs += ensemble
#         segments_result.append({
#             "seg":        seg_idx + 1,
#             "start_t":    start_sec,
#             "end_t":      end_sec,
#             "prediction": ECG_CLASS_NAMES[class_idx],
#             "confidence": round(float(ensemble[class_idx]), 4),
#         })
#     avg_probs    = all_class_probs / n_segments
#     top_idx      = int(np.argmax(avg_probs))
#     normal_count = sum(1 for s in segments_result if s["prediction"] == "Normal")
#     return {
#         "top_condition":  ECG_CLASS_NAMES[top_idx],
#         "top_prob":       round(float(avg_probs[top_idx]) * 100, 2),
#         "normal_count":   normal_count,
#         "abnormal_count": n_segments - normal_count,
#         "total_segments": n_segments,
#         "class_probs": {
#             ECG_CLASS_NAMES[i]: round(float(avg_probs[i]) * 100, 2)
#             for i in range(len(ECG_CLASS_NAMES))
#         },
#         "segments": segments_result,
#     }


# # ── Startup ───────────────────────────────────────────────────────────────────
# @app.on_event("startup")
# async def startup_event():
#     global resnet_model, inception_model, transformer_model

#     await init_db_indexes()
#     logger.info("✅ MongoDB indexes created")

#     # Google Drive File IDs
#     DRIVE_MODELS = [
#         ("resnet_model",      "resnet.keras",      "17td7VKujruuvy4aP0u06B-GCTo9yMquH"),
#         ("inception_model",   "inception.keras",   "1lC_gB_-3qR664ic5fUvpY6OZMhriJbKX"),
#         ("transformer_model", "transformer.keras",  "1I5IdZU2Fskl1YOQrzW8CS0UGzYEFgyw6"),
#     ]

#     # ✅ FIX 4: Safe per-model loading — one failure won't crash others
#     for var_name, filename, file_id in DRIVE_MODELS:
#         try:
#             loaded = download_model(file_id, filename)
#             if var_name == "resnet_model":
#                 resnet_model = loaded
#             elif var_name == "inception_model":
#                 inception_model = loaded
#             else:
#                 transformer_model = loaded
#             logger.info(f"✅ {var_name} ready")
#         except Exception as e:
#             logger.error(f"❌ Failed to load {var_name}: {e}")

#     logger.info("🚀 HealthBridge API startup complete")


# # ── API Routes ────────────────────────────────────────────────────────────────
# @app.post("/api/signup")
# async def signup(user: UserSignup):
#     existing = await users_col.find_one({"user_id": user.user_id})
#     if existing:
#         raise HTTPException(status_code=400, detail="User ID already registered.")
#     user_doc = user.dict()
#     # ✅ FIX 5: Password stored as-is for now — upgrade to bcrypt in production
#     user_doc["password_hash"] = user_doc.pop("password")
#     user_doc["created_at"]    = datetime.utcnow()
#     await users_col.insert_one(user_doc)
#     return {"status": "success", "message": "Account created successfully"}


# @app.post("/api/login")
# async def login(data: dict):
#     user = await users_col.find_one({
#         "user_id":       data['user_id'],
#         "password_hash": data['password']
#     })
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"user_id": user['user_id'], "name": user['name'], "role": user['role']}


# @app.post("/api/predict")
# async def predict(input_data: HealthInput):
#     if not MODEL_LOADED:
#         raise HTTPException(status_code=503, detail="Disease prediction model not available.")
#     raw_features = [
#         input_data.temperature, input_data.heart_rate, input_data.bp_sys,
#         input_data.bp_dia, input_data.humidity, input_data.fever,
#         input_data.cough, input_data.chest_pain, input_data.shortness_breath,
#         input_data.fatigue, input_data.headache
#     ]
#     df = pd.DataFrame([raw_features], columns=feature_names)
#     df[numerical_cols] = scaler.transform(df[numerical_cols])
#     proba   = model.predict(df.values, verbose=0)
#     disease = label_encoder.inverse_transform([np.argmax(proba)])[0]
#     score   = round(float(np.max(proba)) * 100, 2)
#     advice  = get_clinical_advice(disease, score)
#     pred_doc = {
#         "user_id":          input_data.user_id,
#         "service_type":     "AI Checkup",
#         "result_status":    disease,
#         "analysis_score":   score,
#         "temperature":      input_data.temperature,
#         "heart_rate":       input_data.heart_rate,
#         "bp_sys":           input_data.bp_sys,
#         "bp_dia":           input_data.bp_dia,
#         "humidity":         input_data.humidity,
#         "fever":            input_data.fever,
#         "cough":            input_data.cough,
#         "chest_pain":       input_data.chest_pain,
#         "shortness_breath": input_data.shortness_breath,
#         "fatigue":          input_data.fatigue,
#         "headache":         input_data.headache,
#         "suggested_drugs":  advice['drugs'],
#         "suggested_foods":  advice['foods'],
#         "clinical_routine": advice['routine'],
#         "created_at":       datetime.utcnow()
#     }
#     await predictions_col.insert_one(pred_doc)
#     return {"prediction": disease, "score": score, **advice}


# @app.post("/api/ecg-predict")
# async def ecg_predict(
#     file:       UploadFile    = File(...),
#     user_id:    str           = Form(...),
#     start_time: Optional[str] = Form(None)
# ):
#     filename = file.filename or ""
#     ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
#     if ext not in ('csv', 'txt'):
#         raise HTTPException(status_code=400, detail="Only .csv and .txt files supported.")
#     content_bytes = await file.read()
#     try:
#         content = content_bytes.decode('utf-8', errors='ignore')
#     except Exception:
#         raise HTTPException(status_code=400, detail="Cannot decode file.")
#     signal = parse_ecg_csv(content)
#     if signal is None or len(signal) == 0:
#         raise HTTPException(status_code=400, detail="No numeric values found.")
#     if len(signal) < ECG_WINDOW_SIZE:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Signal too short. Need ≥ {ECG_WINDOW_SIZE} samples."
#         )
#     signal = ecg_clean_signal(signal)
#     models = get_ecg_models()
#     try:
#         result = ecg_predict_signal(signal, models)
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"ECG prediction error: {e}")
#         raise HTTPException(status_code=500, detail="Prediction failed")
#     return result


# @app.post("/api/save-ecg-report")
# async def save_ecg_report(data: SaveEcgReportRequest):
#     user = await users_col.find_one({"user_id": data.user_id})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     report_doc = {
#         "user_id":          data.user_id,
#         "service_type":     "ECG Test",
#         "report_type":      data.report_type,
#         "result_status":    data.result_status,
#         "analysis_score":   float(data.analysis_score),
#         "ecg_filename":     data.ecg_filename,
#         "ecg_meta":         data.ecg_meta,
#         "suggested_drugs":  data.suggested_drugs or "",
#         "suggested_foods":  data.suggested_foods or "",
#         "clinical_routine": data.routine or "",
#         "created_at":       datetime.utcnow()
#     }
#     await predictions_col.insert_one(report_doc)
#     return {"status": "success", "message": "ECG report saved."}


# @app.get("/api/reports/{user_id}")
# async def get_reports(user_id: str):
#     cursor  = predictions_col.find({"user_id": user_id}).sort("created_at", -1)
#     reports = await cursor.to_list(length=100)
#     for r in reports:
#         r["_id"] = str(r["_id"])
#         if "created_at" in r:
#             r["created_at"] = r["created_at"].isoformat()
#     return reports


# @app.get("/api/search-patient")
# async def search_patient(q: str = ""):
#     query = {"role": "patient"}
#     if q:
#         query["$or"] = [
#             {"name":    {"$regex": q, "$options": "i"}},
#             {"user_id": {"$regex": q, "$options": "i"}}
#         ]
#     cursor   = users_col.find(query, {"user_id": 1, "name": 1, "role": 1, "_id": 0})
#     patients = await cursor.to_list(length=100)
#     return [{"id_str": p["user_id"], "user_id": p["user_id"], "name": p["name"]} for p in patients]


# @app.delete("/api/delete-patient/{patient_id}")
# async def delete_patient(patient_id: str):
#     await predictions_col.delete_many({"user_id": patient_id})
#     await feedback_col.delete_many({"patient_id": patient_id})
#     await users_col.delete_one({"user_id": patient_id})
#     return {"status": "success"}


# @app.post("/api/send-feedback")
# async def send_feedback(data: dict):
#     fb_doc = {
#         "doctor_id":     data['doctor_id'],
#         "patient_id":    data['patient_id'],
#         "message":       data['message'],
#         "prescribed_at": datetime.utcnow()
#     }
#     await feedback_col.insert_one(fb_doc)
#     return {"status": "success"}


# @app.get("/api/get-feedback/{patient_id}")
# async def get_feedback(patient_id: str):
#     fb = await feedback_col.find_one(
#         {"patient_id": patient_id},
#         sort=[("prescribed_at", -1)]
#     )
#     if fb:
#         return {"message": fb["message"]}
#     return {"message": "No clinical instructions deployed yet."}


# @app.post("/api/contact")
# async def save_contact_message(contact: ContactMessage):
#     await contact_col.insert_one(contact.dict())
#     return {"status": "success", "message": "Inquiry transmitted successfully."}


# @app.get("/api/doctor-stats")
# async def get_doctor_stats():
#     total_patients = await users_col.count_documents({"role": "patient"})
#     total_checks   = await predictions_col.count_documents({})
#     responded      = len(await feedback_col.distinct("patient_id"))
#     return {
#         "total_patients": total_patients,
#         "total_checks":   total_checks,
#         "responded":      responded,
#         "pending":        total_patients - responded
#     }


# @app.get("/api/doctor-patient-list")
# async def get_doctor_patient_list():
#     patients = await users_col.find(
#         {"role": "patient"}, {"user_id": 1, "name": 1}
#     ).to_list(length=1000)
#     result = []
#     for p in patients:
#         latest = await predictions_col.find_one(
#             {"user_id": p["user_id"]},
#             sort=[("created_at", -1)]
#         )
#         if latest:
#             result.append({
#                 "id_str":         p["user_id"],
#                 "name":           p["name"],
#                 "latest_disease": latest.get("result_status", ""),
#                 "latest_risk":    latest.get("analysis_score"),
#                 "latest_date":    latest["created_at"].isoformat() if latest.get("created_at") else None
#             })
#         else:
#             result.append({
#                 "id_str":         p["user_id"],
#                 "name":           p["name"],
#                 "latest_disease": "No checkup yet",
#                 "latest_risk":    None,
#                 "latest_date":    None
#             })
#     return result


# @app.get("/api/patient-stats/{user_id}")
# async def get_patient_stats(user_id: str):
#     pipeline = [
#         {"$match": {"user_id": user_id}},
#         {"$group": {"_id": "$result_status", "count": {"$sum": 1}}},
#         {"$sort":  {"count": -1}}
#     ]
#     stats        = await predictions_col.aggregate(pipeline).to_list(length=20)
#     total        = await predictions_col.count_documents({"user_id": user_id})
#     disease_dist = [{"disease": s["_id"], "count": s["count"]} for s in stats]
#     return {"total_visits": total, "disease_distribution": disease_dist}


# @app.post("/api/chatbot")
# async def chatbot(request: ChatbotRequest):
#     user = await users_col.find_one({"user_id": request.user_id})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     reports = await predictions_col.find(
#         {"user_id": request.user_id}
#     ).sort("created_at", -1).to_list(length=10)
#     if reports:
#         lines = ["Patient's medical history (most recent first):"]
#         for r in reports:
#             date_str = r['created_at'].strftime("%Y-%m-%d %H:%M") if r.get('created_at') else "Unknown"
#             lines.append(
#                 f"- {date_str}: {r.get('result_status','')} "
#                 f"(Risk: {r.get('analysis_score','')}%) | "
#                 f"Drugs: {r.get('suggested_drugs','')} | "
#                 f"Foods: {r.get('suggested_foods','')} | "
#                 f"Routine: {r.get('clinical_routine','')}"
#             )
#         context = "\n".join(lines)
#     else:
#         context = "No previous medical reports available."
#     prompt = (
#         "You are a helpful medical assistant. Based on the following patient history, "
#         "answer the user's question.\n\n"
#         f"{context}\n\n"
#         f"User question: {request.message}\n\n"
#         "Provide a concise, informative answer."
#     )
#     groq_api_key = os.getenv("GROQ_API_KEY")
#     if not groq_api_key:
#         raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment")
#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             json={
#                 "model": "llama-3.3-70b-versatile",
#                 "messages": [
#                     {"role": "system", "content": "You are a helpful medical assistant."},
#                     {"role": "user",   "content": prompt}
#                 ],
#                 "temperature": 0.2,
#                 "max_tokens":  500
#             },
#             headers={"Authorization": f"Bearer {groq_api_key}"}
#         )
#         if response.status_code == 429:
#             return {"reply": "High demand. Please try again later."}
#         if response.status_code != 200:
#             raise HTTPException(status_code=502, detail="AI service unavailable")
#         data  = response.json()
#         reply = data['choices'][0]['message']['content']
#     return {"reply": reply}


# # ✅ FIX 3: Correct host="0.0.0.0" and dynamic PORT for Render
# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 10000))
#     uvicorn.run(app, host="0.0.0.0", port=port)


import os
import sys
import pickle
import json
import logging
import httpx
import numpy as np
import pandas as pd
import gdown
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, model_validator, root_validator
from dotenv import load_dotenv

from scipy.signal import butter, filtfilt, iirnotch
import tensorflow as tf
from tensorflow.keras import layers

sys.path.append(str(Path(__file__).parent))

from database import (
    db, users_col, predictions_col, feedback_col, contact_col, init_db_indexes
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HealthBridge API V6.0 - MongoDB Atlas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# ✅ FIX 1: MODEL_PATH now inside repo → backend/model/model_saved.pkl
MODEL_PATH = BASE_DIR / "model" / "model_saved.pkl"

# ✅ ECG models download folder (auto-created)
ECG_MODEL_DIR = BASE_DIR / "models"
ECG_MODEL_DIR.mkdir(parents=True, exist_ok=True)

ECG_WINDOW_SIZE  = 3600
ECG_SAMPLING_RATE = 360
ECG_CLASS_NAMES  = [
    "Normal", "Supraventricular", "Ventricular",
    "Conduction Disorder", "Myocardial Infarction",
    "Hypertrophy", "Ischemia/ST-T", "Atrial Fibrillation"
]
W_RESNET, W_INCEPTION, W_TRANSFORMER = 0.45, 0.35, 0.20

# ── Disease prediction model ──────────────────────────────────────────────────
try:
    with open(MODEL_PATH, "rb") as f:
        package = pickle.load(f)
    model         = package["model"]
    scaler        = package["scaler"]
    label_encoder = package["label_encoder"]
    feature_names = package["feature_names"]
    numerical_cols = package["numerical_cols"]
    MODEL_LOADED  = True
    logger.info("✅ Disease Prediction Model Loaded")
except Exception as e:
    MODEL_LOADED  = False
    logger.error(f"❌ Disease model load failed: {e}")


# ── Custom Keras layer ────────────────────────────────────────────────────────
@tf.keras.utils.register_keras_serializable()
class PositionalEncoding(layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, x):
        seq_len     = tf.shape(x)[1]
        d_model     = tf.shape(x)[2]
        positions   = tf.range(seq_len, dtype=tf.float32)[:, tf.newaxis]
        dims        = tf.range(d_model,  dtype=tf.float32)[tf.newaxis, :]
        angle_rates = 1 / tf.pow(10000.0, (2 * (dims // 2)) / tf.cast(d_model, tf.float32))
        angles      = positions * angle_rates
        even_mask   = tf.cast(tf.math.floormod(dims, 2) == 0, tf.float32)
        odd_mask    = 1 - even_mask
        angles      = tf.sin(angles) * even_mask + tf.cos(angles) * odd_mask
        return x + angles[tf.newaxis, :, :]

    def get_config(self):
        return super().get_config()


# ── Google Drive downloader ───────────────────────────────────────────────────
def download_model(file_id: str, filename: str):
    """Download model from Google Drive if not cached, then load it."""
    path = ECG_MODEL_DIR / filename
    if not path.exists():
        logger.info(f"⬇️  Downloading {filename} from Google Drive …")
        gdown.download(f"https://drive.google.com/uc?id={file_id}", str(path), quiet=False)
        logger.info(f"✅ Downloaded: {filename}")
    else:
        logger.info(f"✅ Cached model found: {filename}")
    return tf.keras.models.load_model(
        str(path),
        custom_objects={"PositionalEncoding": PositionalEncoding}
    )


# ── Global ECG model references ───────────────────────────────────────────────
resnet_model      = None
inception_model   = None
transformer_model = None


def get_ecg_models() -> dict:
    if resnet_model is None or inception_model is None or transformer_model is None:
        raise HTTPException(
            status_code=503,
            detail="ECG models not loaded yet. Please retry in a moment."
        )
    return {
        "resnet":      resnet_model,
        "inception":   inception_model,
        "transformer": transformer_model,
    }


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class ContactMessage(BaseModel):
    full_name:  str
    medical_id: Optional[str]      = None
    email:      Optional[EmailStr] = None
    phone:      Optional[str]      = None
    subject:    Optional[str]      = None
    message:    Optional[str]      = None

    @model_validator(mode='after')
    def validate_communication_method(self):
        if not self.email and not self.phone:
            raise ValueError('Either Email or Phone is required.')
        return self


class UserSignup(BaseModel):
    user_id:     str
    name:        str
    email:       Optional[str] = None
    phone:       Optional[str] = None
    role:        str
    password:    str
    dept:        Optional[str] = None
    blood_group: Optional[str] = None

    @root_validator(pre=True)
    def check_contact_info(cls, values):
        if not values.get('email') and not values.get('phone'):
            raise ValueError('Either email or phone must be provided')
        return values


class HealthInput(BaseModel):
    user_id:          str
    temperature:      float
    heart_rate:       float
    bp_dia:           float
    bp_sys:           float
    humidity:         float
    fever:            int
    cough:            int
    chest_pain:       int
    shortness_breath: int
    fatigue:          int
    headache:         int


class ChatbotRequest(BaseModel):
    user_id: str
    message: str


class SaveEcgReportRequest(BaseModel):
    user_id:         str
    report_type:     str           = "ecg"
    result_status:   str
    analysis_score:  float
    ecg_filename:    Optional[str] = None
    ecg_meta:        Optional[str] = None
    suggested_drugs: Optional[str] = ""
    suggested_foods: Optional[str] = ""
    routine:         Optional[str] = ""


# ── Clinical advice helper ────────────────────────────────────────────────────
def get_clinical_advice(disease: str, score: float) -> dict:
    advice = {"drugs": "Consult Doctor", "foods": "Balanced Diet", "routine": "Rest"}
    if disease == "Heart_Risk":
        if 60 <= score < 80:
            advice = {
                "drugs":   "Aspirin (75mg) - 1 tab after lunch; Atorvastatin (10mg) - 1 tab at night",
                "foods":   "Walnuts, Oats, Garlic, Low-sodium meals",
                "routine": "Avoid heavy lifting, 15 min slow walk"
            }
        elif score >= 80:
            advice = {
                "drugs":   "Nitroglycerin (emergency); Clopidogrel (75mg) - 1 tab daily",
                "foods":   "Strict heart-healthy diet, Fatty fish, Zero added salt",
                "routine": "Immediate cardiology consultation. Complete bed rest"
            }
    elif disease == "Fever_Respiratory":
        if score < 80:
            advice = {
                "drugs":   "Paracetamol (500mg) - 1 tab after meals (max 3/day)",
                "foods":   "Warm soup, Citrus fruits, Ginger tea",
                "routine": "Steam inhalation twice daily"
            }
        else:
            advice = {
                "drugs":   "Paracetamol (650mg) - every 6h; Azithromycin (500mg) - 1 tab daily",
                "foods":   "High-protein soft diet, ORS, Honey-lemon water",
                "routine": "Strict isolation. Monitor SpO2 levels"
            }
    elif disease == "Hypertension":
        if 60 <= score < 80:
            advice = {
                "drugs":   "Amlodipine (5mg) - 1 tab morning",
                "foods":   "Bananas, Spinach, Skim milk. Avoid raw salt",
                "routine": "30 mins brisk walking. No nicotine"
            }
        else:
            advice = {
                "drugs":   "Losartan (50mg) daily; Hydrochlorothiazide (12.5mg) morning",
                "foods":   "Beetroot juice, Pomegranate. Zero added salt",
                "routine": "Stress management (Yoga). Regular BP monitoring"
            }
    elif disease == "Hypotension":
        advice = {
            "drugs":   "ORS (1L throughout day); Vitamin B12 supplements",
            "foods":   "Cheese, Olives, Salty snacks (moderate), Coffee",
            "routine": "Elevate legs while resting. Avoid sudden movements"
        }
    return advice


# ── ECG signal helpers ────────────────────────────────────────────────────────
def ecg_preprocess_window(signal: np.ndarray, fs: int = ECG_SAMPLING_RATE) -> np.ndarray:
    nyq  = 0.5 * fs
    low  = 0.5 / nyq
    high = min(45.0 / nyq, 0.99)
    b, a = butter(3, [low, high], btype='bandpass')
    sig  = filtfilt(b, a, signal)
    w0   = 50.0 / nyq
    if w0 < 1.0:
        bn, an = iirnotch(w0, 30)
        sig = filtfilt(bn, an, sig)
    mean = np.mean(sig)
    std  = np.std(sig)
    return ((sig - mean) / (std + 1e-8)).astype(np.float32)


def ecg_clean_signal(signal: np.ndarray) -> np.ndarray:
    bad_mask  = np.abs(signal - 512) <= 5
    bad_mask |= (signal <= 2) | (signal >= 1021)
    if np.any(bad_mask):
        indices  = np.arange(len(signal))
        good_idx = indices[~bad_mask]
        good_val = signal[~bad_mask]
        if len(good_val) >= 2:
            signal[bad_mask] = np.interp(indices[bad_mask], good_idx, good_val)
    return signal


def parse_ecg_csv(content: str) -> Optional[np.ndarray]:
    try:
        lines  = content.replace(',', ' ').replace('\t', ' ').strip().splitlines()
        values = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            for tok in line.split():
                try:
                    v = float(tok)
                    if np.isfinite(v):
                        values.append(v)
                except ValueError:
                    continue
        return np.array(values, dtype=np.float64) if values else None
    except Exception:
        return None


def ecg_predict_signal(signal: np.ndarray, models: dict) -> dict:
    n_segments = int(len(signal) // ECG_WINDOW_SIZE)
    if n_segments == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Signal too short. Need ≥ {ECG_WINDOW_SIZE} samples."
        )
    all_class_probs = np.zeros(len(ECG_CLASS_NAMES))
    segments_result = []
    for seg_idx in range(n_segments):
        start     = seg_idx * ECG_WINDOW_SIZE
        end       = start + ECG_WINDOW_SIZE
        start_sec = round(start / ECG_SAMPLING_RATE, 1)
        end_sec   = round(end   / ECG_SAMPLING_RATE, 1)
        window    = ecg_preprocess_window(signal[start:end].copy())
        x         = window.reshape(1, ECG_WINDOW_SIZE, 1).astype(np.float32)
        p_r = models["resnet"].predict(x,      verbose=0)[0]
        p_i = models["inception"].predict(x,   verbose=0)[0]
        p_t = models["transformer"].predict(x, verbose=0)[0]
        ensemble  = W_RESNET * p_r + W_INCEPTION * p_i + W_TRANSFORMER * p_t
        class_idx = int(np.argmax(ensemble))
        all_class_probs += ensemble
        segments_result.append({
            "seg":        seg_idx + 1,
            "start_t":    start_sec,
            "end_t":      end_sec,
            "prediction": ECG_CLASS_NAMES[class_idx],
            "confidence": round(float(ensemble[class_idx]), 4),
        })
    avg_probs    = all_class_probs / n_segments
    top_idx      = int(np.argmax(avg_probs))
    normal_count = sum(1 for s in segments_result if s["prediction"] == "Normal")
    return {
        "top_condition":  ECG_CLASS_NAMES[top_idx],
        "top_prob":       round(float(avg_probs[top_idx]) * 100, 2),
        "normal_count":   normal_count,
        "abnormal_count": n_segments - normal_count,
        "total_segments": n_segments,
        "class_probs": {
            ECG_CLASS_NAMES[i]: round(float(avg_probs[i]) * 100, 2)
            for i in range(len(ECG_CLASS_NAMES))
        },
        "segments": segments_result,
    }


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    global resnet_model, inception_model, transformer_model

    await init_db_indexes()
    logger.info("✅ MongoDB indexes created")

    # Google Drive File IDs
    DRIVE_MODELS = [
        ("resnet_model",      "resnet.keras",      "17td7VKujruuvy4aP0u06B-GCTo9yMquH"),
        ("inception_model",   "inception.keras",   "1lC_gB_-3qR664ic5fUvpY6OZMhriJbKX"),
        ("transformer_model", "transformer.keras",  "1I5IdZU2Fskl1YOQrzW8CS0UGzYEFgyw6"),
    ]

    # ✅ FIX 4: Safe per-model loading — one failure won't crash others
    for var_name, filename, file_id in DRIVE_MODELS:
        try:
            loaded = download_model(file_id, filename)
            if var_name == "resnet_model":
                resnet_model = loaded
            elif var_name == "inception_model":
                inception_model = loaded
            else:
                transformer_model = loaded
            logger.info(f"✅ {var_name} ready")
        except Exception as e:
            logger.error(f"❌ Failed to load {var_name}: {e}")

    logger.info("🚀 HealthBridge API startup complete")


# ── API Routes ────────────────────────────────────────────────────────────────
@app.post("/api/signup")
async def signup(user: UserSignup):
    existing = await users_col.find_one({"user_id": user.user_id})
    if existing:
        raise HTTPException(status_code=400, detail="User ID already registered.")
    user_doc = user.dict()
    # ✅ FIX 5: Password stored as-is for now — upgrade to bcrypt in production
    user_doc["password_hash"] = user_doc.pop("password")
    user_doc["created_at"]    = datetime.utcnow()
    await users_col.insert_one(user_doc)
    return {"status": "success", "message": "Account created successfully"}


@app.post("/api/login")
async def login(data: dict):
    user = await users_col.find_one({
        "user_id":       data['user_id'],
        "password_hash": data['password']
    })
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": user['user_id'], "name": user['name'], "role": user['role']}


@app.post("/api/predict")
async def predict(input_data: HealthInput):
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Disease prediction model not available.")
    raw_features = [
        input_data.temperature, input_data.heart_rate, input_data.bp_sys,
        input_data.bp_dia, input_data.humidity, input_data.fever,
        input_data.cough, input_data.chest_pain, input_data.shortness_breath,
        input_data.fatigue, input_data.headache
    ]
    df = pd.DataFrame([raw_features], columns=feature_names)
    df[numerical_cols] = scaler.transform(df[numerical_cols])
    proba   = model.predict(df.values, verbose=0)
    disease = label_encoder.inverse_transform([np.argmax(proba)])[0]
    score   = round(float(np.max(proba)) * 100, 2)
    advice  = get_clinical_advice(disease, score)
    pred_doc = {
        "user_id":          input_data.user_id,
        "service_type":     "AI Checkup",
        "result_status":    disease,
        "analysis_score":   score,
        "temperature":      input_data.temperature,
        "heart_rate":       input_data.heart_rate,
        "bp_sys":           input_data.bp_sys,
        "bp_dia":           input_data.bp_dia,
        "humidity":         input_data.humidity,
        "fever":            input_data.fever,
        "cough":            input_data.cough,
        "chest_pain":       input_data.chest_pain,
        "shortness_breath": input_data.shortness_breath,
        "fatigue":          input_data.fatigue,
        "headache":         input_data.headache,
        "suggested_drugs":  advice['drugs'],
        "suggested_foods":  advice['foods'],
        "clinical_routine": advice['routine'],
        "created_at":       datetime.utcnow()
    }
    await predictions_col.insert_one(pred_doc)
    return {"prediction": disease, "score": score, **advice}


@app.post("/api/ecg-predict")
async def ecg_predict(
    file:       UploadFile    = File(...),
    user_id:    str           = Form(...),
    start_time: Optional[str] = Form(None)
):
    import traceback

    # ── STEP 1: Validate file extension ──────────────────────────────────────
    try:
        filename = file.filename or ""
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        logger.info(f"📥 ECG upload: file='{filename}' user='{user_id}'  ext='{ext}'" )
        if ext not in ('csv', 'txt'):
            raise HTTPException(status_code=400, detail="Only .csv and .txt files supported.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("STEP1 error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"File validation error: {str(e)}")

    # ── STEP 2: Read & decode file bytes ─────────────────────────────────────
    try:
        content_bytes = await file.read()
        logger.info(f"📄 File size: {len(content_bytes)} bytes")
        content = content_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error("STEP2 error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Cannot decode file: {str(e)}")

    # ── STEP 3: Parse CSV → numpy signal ─────────────────────────────────────
    try:
        signal = parse_ecg_csv(content)
        if signal is None or len(signal) == 0:
            raise HTTPException(status_code=400, detail="No numeric values found in file.")
        logger.info(f"📊 Signal parsed: {len(signal)} samples  min={signal.min():.2f}  max={signal.max():.2f}")
        if len(signal) < ECG_WINDOW_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Signal too short ({len(signal)} samples). Need ≥ {ECG_WINDOW_SIZE} samples ({ECG_WINDOW_SIZE/ECG_SAMPLING_RATE:.0f}s at {ECG_SAMPLING_RATE}Hz)."
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("STEP3 error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Signal parsing error: {str(e)}")

    # ── STEP 4: Clean signal artifacts ───────────────────────────────────────
    try:
        signal = ecg_clean_signal(signal)
        logger.info(f"🧹 Signal cleaned: {len(signal)} samples")
    except Exception as e:
        logger.error("STEP4 error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Signal cleaning error: {str(e)}")

    # ── STEP 5: Check models are loaded ──────────────────────────────────────
    try:
        models = get_ecg_models()
        logger.info("🤖 ECG models retrieved successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("STEP5 error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=503, detail=f"Model retrieval error: {str(e)}")

    # ── STEP 6: Run ensemble prediction ──────────────────────────────────────
    try:
        n_segments = int(len(signal) // ECG_WINDOW_SIZE)
        logger.info(f"🔬 Running prediction on {n_segments} segment(s) …")
        result = ecg_predict_signal(signal, models)
        logger.info(f"✅ Prediction done: top={result['top_condition']}  prob={result['top_prob']}%")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("STEP6 prediction error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    return result


@app.post("/api/save-ecg-report")
async def save_ecg_report(data: SaveEcgReportRequest):
    user = await users_col.find_one({"user_id": data.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    report_doc = {
        "user_id":          data.user_id,
        "service_type":     "ECG Test",
        "report_type":      data.report_type,
        "result_status":    data.result_status,
        "analysis_score":   float(data.analysis_score),
        "ecg_filename":     data.ecg_filename,
        "ecg_meta":         data.ecg_meta,
        "suggested_drugs":  data.suggested_drugs or "",
        "suggested_foods":  data.suggested_foods or "",
        "clinical_routine": data.routine or "",
        "created_at":       datetime.utcnow()
    }
    await predictions_col.insert_one(report_doc)
    return {"status": "success", "message": "ECG report saved."}


@app.get("/api/reports/{user_id}")
async def get_reports(user_id: str):
    cursor  = predictions_col.find({"user_id": user_id}).sort("created_at", -1)
    reports = await cursor.to_list(length=100)
    for r in reports:
        r["_id"] = str(r["_id"])
        if "created_at" in r:
            r["created_at"] = r["created_at"].isoformat()
    return reports


@app.get("/api/search-patient")
async def search_patient(q: str = ""):
    query = {"role": "patient"}
    if q:
        query["$or"] = [
            {"name":    {"$regex": q, "$options": "i"}},
            {"user_id": {"$regex": q, "$options": "i"}}
        ]
    cursor   = users_col.find(query, {"user_id": 1, "name": 1, "role": 1, "_id": 0})
    patients = await cursor.to_list(length=100)
    return [{"id_str": p["user_id"], "user_id": p["user_id"], "name": p["name"]} for p in patients]


@app.delete("/api/delete-patient/{patient_id}")
async def delete_patient(patient_id: str):
    await predictions_col.delete_many({"user_id": patient_id})
    await feedback_col.delete_many({"patient_id": patient_id})
    await users_col.delete_one({"user_id": patient_id})
    return {"status": "success"}


@app.post("/api/send-feedback")
async def send_feedback(data: dict):
    fb_doc = {
        "doctor_id":     data['doctor_id'],
        "patient_id":    data['patient_id'],
        "message":       data['message'],
        "prescribed_at": datetime.utcnow()
    }
    await feedback_col.insert_one(fb_doc)
    return {"status": "success"}


@app.get("/api/get-feedback/{patient_id}")
async def get_feedback(patient_id: str):
    fb = await feedback_col.find_one(
        {"patient_id": patient_id},
        sort=[("prescribed_at", -1)]
    )
    if fb:
        return {"message": fb["message"]}
    return {"message": "No clinical instructions deployed yet."}


@app.post("/api/contact")
async def save_contact_message(contact: ContactMessage):
    await contact_col.insert_one(contact.dict())
    return {"status": "success", "message": "Inquiry transmitted successfully."}


@app.get("/api/doctor-stats")
async def get_doctor_stats():
    total_patients = await users_col.count_documents({"role": "patient"})
    total_checks   = await predictions_col.count_documents({})
    responded      = len(await feedback_col.distinct("patient_id"))
    return {
        "total_patients": total_patients,
        "total_checks":   total_checks,
        "responded":      responded,
        "pending":        total_patients - responded
    }


@app.get("/api/doctor-patient-list")
async def get_doctor_patient_list():
    patients = await users_col.find(
        {"role": "patient"}, {"user_id": 1, "name": 1}
    ).to_list(length=1000)
    result = []
    for p in patients:
        latest = await predictions_col.find_one(
            {"user_id": p["user_id"]},
            sort=[("created_at", -1)]
        )
        if latest:
            result.append({
                "id_str":         p["user_id"],
                "name":           p["name"],
                "latest_disease": latest.get("result_status", ""),
                "latest_risk":    latest.get("analysis_score"),
                "latest_date":    latest["created_at"].isoformat() if latest.get("created_at") else None
            })
        else:
            result.append({
                "id_str":         p["user_id"],
                "name":           p["name"],
                "latest_disease": "No checkup yet",
                "latest_risk":    None,
                "latest_date":    None
            })
    return result


@app.get("/api/patient-stats/{user_id}")
async def get_patient_stats(user_id: str):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$result_status", "count": {"$sum": 1}}},
        {"$sort":  {"count": -1}}
    ]
    stats        = await predictions_col.aggregate(pipeline).to_list(length=20)
    total        = await predictions_col.count_documents({"user_id": user_id})
    disease_dist = [{"disease": s["_id"], "count": s["count"]} for s in stats]
    return {"total_visits": total, "disease_distribution": disease_dist}


@app.post("/api/chatbot")
async def chatbot(request: ChatbotRequest):
    user = await users_col.find_one({"user_id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reports = await predictions_col.find(
        {"user_id": request.user_id}
    ).sort("created_at", -1).to_list(length=10)
    if reports:
        lines = ["Patient's medical history (most recent first):"]
        for r in reports:
            date_str = r['created_at'].strftime("%Y-%m-%d %H:%M") if r.get('created_at') else "Unknown"
            lines.append(
                f"- {date_str}: {r.get('result_status','')} "
                f"(Risk: {r.get('analysis_score','')}%) | "
                f"Drugs: {r.get('suggested_drugs','')} | "
                f"Foods: {r.get('suggested_foods','')} | "
                f"Routine: {r.get('clinical_routine','')}"
            )
        context = "\n".join(lines)
    else:
        context = "No previous medical reports available."
    prompt = (
        "You are a helpful medical assistant. Based on the following patient history, "
        "answer the user's question.\n\n"
        f"{context}\n\n"
        f"User question: {request.message}\n\n"
        "Provide a concise, informative answer."
    )
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user",   "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens":  500
            },
            headers={"Authorization": f"Bearer {groq_api_key}"}
        )
        if response.status_code == 429:
            return {"reply": "High demand. Please try again later."}
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="AI service unavailable")
        data  = response.json()
        reply = data['choices'][0]['message']['content']
    return {"reply": reply}


# ✅ FIX 3: Correct host="0.0.0.0" and dynamic PORT for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)