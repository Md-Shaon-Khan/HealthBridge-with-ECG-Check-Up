// ============================================================
//  HealthBridge — Central API Configuration
//  👉 Import this file in EVERY JS file that calls the backend
//  👉 Never use localhost in fetch() calls directly
// ============================================================

const API_BASE = "https://api.ecg-iit-ju-shaon.xyz";

// ── Auth ──────────────────────────────────────────────────────
const API = {
  login: `${API_BASE}/api/login`,
  signup: `${API_BASE}/api/signup`,

  // ── Health prediction ────────────────────────────────────────
  predict: `${API_BASE}/api/predict`,

  // ── ECG ──────────────────────────────────────────────────────
  ecgPredict: `${API_BASE}/api/ecg-predict`,
  saveEcgReport: `${API_BASE}/api/save-ecg-report`,

  // ── Reports ──────────────────────────────────────────────────
  reports: (userId) => `${API_BASE}/api/reports/${userId}`,

  // ── Doctor panel ─────────────────────────────────────────────
  doctorStats: `${API_BASE}/api/doctor-stats`,
  doctorPatientList: `${API_BASE}/api/doctor-patient-list`,
  searchPatient: (q) => `${API_BASE}/api/search-patient?q=${q}`,
  deletePatient: (id) => `${API_BASE}/api/delete-patient/${id}`,

  // ── Patient ──────────────────────────────────────────────────
  patientStats: (userId) => `${API_BASE}/api/patient-stats/${userId}`,
  getFeedback: (userId) => `${API_BASE}/api/get-feedback/${userId}`,
  sendFeedback: `${API_BASE}/api/send-feedback`,

  // ── Chatbot & Contact ─────────────────────────────────────────
  chatbot: `${API_BASE}/api/chatbot`,
  contact: `${API_BASE}/api/contact`,
};