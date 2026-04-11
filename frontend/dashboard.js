/**
 * HealthBridge | Clinical Command Center Logic V10.0
 * Features: Role-based default section, active link styling,
 *           ECG Test: file upload, signal preview, AI analysis,
 *           save to My Reports, doctor ECG history view.
 *           Enhanced: two random 10s segment graphs, start time input,
 *           abnormal event clock times.
 */

// ─── ECG constants (must match backend / predict_master.py) ───
const ECG_SAMPLING_RATE = 360;
const ECG_WINDOW_SIZE = ECG_SAMPLING_RATE * 10; // 3 600 samples = 10 s
const ECG_CLASS_NAMES = [
    "Normal", "Supraventricular", "Ventricular",
    "Conduction", "MI", "Hypertrophy", "Ischemia", "AF"
];
const ECG_CLASS_COLORS = {
    "Normal": "#2ecc71",
    "Supraventricular": "#3498db",
    "Ventricular": "#e74c3c",
    "Conduction": "#f39c12",
    "MI": "#e67e22",
    "Hypertrophy": "#9b59b6",
    "Ischemia": "#c0392b",
    "AF": "#e91e8c",
};

// ─── ECG state ────────────────────────────────────────────────
let ecgSelectedFile = null;   // File object
let ecgRawData = null;   // Float64Array of signal samples
let ecgAnalysisResult = null;   // Result object from backend
let ecgWaveformChart = null;   // Chart.js instance (waveform)
let ecgProbChart = null;   // Chart.js instance (probability bar)
let ecgConfChart = null;   // Chart.js instance (confidence line)
let ecgStartTimeValue = null;   // ISO string from datetime-local input

// ─────────────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const userName = localStorage.getItem('userName') || 'Medical Professional';
    const userId = localStorage.getItem('userId');
    const userRole = localStorage.getItem('userRole') || 'patient';

    document.getElementById('displayUserName').innerText = userName;
    document.getElementById('displayUserId').innerText = `ID: ${userId}`;
    document.getElementById('roleBadge').innerText = userRole.toUpperCase();

    if (userRole === 'doctor') {
        document.getElementById('doctorLinks').classList.remove('hidden');
        document.getElementById('doctorStats').classList.remove('hidden');
        document.getElementById('doctorPatientList').classList.remove('hidden');
        document.getElementById('patientLinks').classList.add('hidden');
        loadDoctorOverview();
        showSection('overview');
    } else {
        document.getElementById('patientStats').classList.remove('hidden');
        showSection('predictor');
        loadPatientOverview();
        loadReports();
        loadPatientHealthTrend();
    }

    document.getElementById('predictForm').addEventListener('submit', handlePredict);

    // Allow pressing Enter in chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    // Click on dropzone (not on the label) opens file picker
    const dropzone = document.getElementById('ecgDropzone');
    if (dropzone) {
        dropzone.addEventListener('click', e => {
            if (e.target.tagName === 'LABEL' || e.target.tagName === 'INPUT') return;
            document.getElementById('ecgFileInput').click();
        });
    }
});

// ─────────────────────────────────────────────────────────────
// SECTION TOGGLER
// ─────────────────────────────────────────────────────────────
function showSection(sectionId) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
    document.getElementById(sectionId).classList.remove('hidden');

    const titles = {
        'overview': 'Overview',
        'predictor': 'AI Predictor',
        'reports': 'My Reports',
        'manage-patients': 'Patient Checkup',
        'chatbot': 'Medical Assistant',
        'ecgtest': 'ECG Test',
    };
    document.getElementById('sectionTitle').innerText = titles[sectionId] || sectionId;

    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(`'${sectionId}'`)) {
            link.classList.add('active');
        }
    });

    if (sectionId === 'manage-patients') {
        loadAllPatients('A');
        loadAllPatients('B');
    }
}

// ─────────────────────────────────────────────────────────────
// PATIENT OVERVIEW
// ─────────────────────────────────────────────────────────────
async function loadPatientOverview() {
    const patientId = localStorage.getItem('userId');
    try {
        const response = await fetch(`https://ecg-4ggp.onrender.com/api/reports/${patientId}`);
        const data = await response.json();

        if (document.getElementById('totalVisits'))
            document.getElementById('totalVisits').innerText = data.length;

        if (data.length > 0) {
            const latest = data[0];
            document.getElementById('latestDisease').innerText = latest.result_status;
            document.getElementById('latestRisk').innerText = latest.analysis_score;
        } else {
            document.getElementById('latestDisease').innerText = '—';
            document.getElementById('latestRisk').innerText = '—';
        }

        const diseaseCounts = {};
        data.forEach(report => {
            const disease = report.result_status;
            diseaseCounts[disease] = (diseaseCounts[disease] || 0) + 1;
        });

        const rankList = document.getElementById('diseaseRank');
        rankList.innerHTML = Object.entries(diseaseCounts)
            .sort((a, b) => b[1] - a[1])
            .map(([name, count]) => `
        <div style="font-size:0.85rem;padding:5px 0;border-bottom:1px solid #f1f5f9;">
          <strong>${name}</strong>: ${count} times
        </div>
      `).join('');

    } catch (err) { console.error("Patient insights failed", err); }
}

// ─────────────────────────────────────────────────────────────
// DOCTOR OVERVIEW
// ─────────────────────────────────────────────────────────────
async function loadDoctorOverview() {
    try {
        const response = await fetch('https://ecg-4ggp.onrender.com/api/doctor-stats');
        const stats = await response.json();

        document.getElementById('totalPatients').innerText = stats.total_patients;
        document.getElementById('totalChecks').innerText = stats.total_checks;
        document.getElementById('respondedCount').innerText = stats.responded;
        document.getElementById('pendingCount').innerText = stats.pending;

        const patientRes = await fetch('https://ecg-4ggp.onrender.com/api/doctor-patient-list');
        const patients = await patientRes.json();
        const container = document.getElementById('patientListContainer');
        container.innerHTML = patients.map(p => `
      <div class="patient-list-item">
        <div>
          <strong>${p.name}</strong> (${p.id_str})<br>
          <small>Latest: ${p.latest_disease} ${p.latest_risk ? '(' + p.latest_risk + '%)' : ''}</small>
        </div>
        ${p.latest_risk
                ? `<span class="risk-badge">Risk ${p.latest_risk}%</span>`
                : '<span class="no-data">No data</span>'}
      </div>
    `).join('');
    } catch (err) { console.error("Doctor insights failed", err); }
}

// ─────────────────────────────────────────────────────────────
// MY REPORTS
// ─────────────────────────────────────────────────────────────
async function loadReports() {
    const patientId = localStorage.getItem('userId');
    const reportList = document.getElementById('patientReportList');

    try {
        const feedbackRes = await fetch(`https://ecg-4ggp.onrender.com/api/get-feedback/${patientId}`);
        const feedback = await feedbackRes.json();
        if (feedback && feedback.message) {
            document.getElementById('doctorMessageArea').classList.remove('hidden');
            document.getElementById('feedbackText').innerText = `"${feedback.message}"`;
        }

        const response = await fetch(`https://ecg-4ggp.onrender.com/api/reports/${patientId}`);
        const reports = await response.json();

        // Separate ECG reports from regular reports
        const regular = reports.filter(r => r.report_type !== 'ecg');
        const ecg = reports.filter(r => r.report_type === 'ecg');

        let html = '';

        if (regular.length > 0) {
            html += `<div class="shell-header" style="margin-bottom:0.5rem;">
                 <span class="label-heading">AI Predictor Reports</span>
               </div>`;
            html += regular.map(r => `
        <div class="summary-card" style="margin-bottom:1rem;border-left:5px solid #8686AC;">
          <h4 style="color:#0A0A23;">${r.result_status} (Risk: ${r.analysis_score}%)</h4>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
            <div style="background:#F1F5F9;padding:10px;border-radius:8px;">
              <strong>Drugs:</strong><br><small>${r.suggested_drugs}</small>
            </div>
            <div style="background:#F1F5F9;padding:10px;border-radius:8px;">
              <strong>Diet:</strong><br><small>${r.suggested_foods}</small>
            </div>
          </div>
          <p style="font-size:0.7rem;margin-top:8px;color:#64748B;">
            Date: ${new Date(r.created_at).toLocaleString()}
          </p>
        </div>
      `).join('');
        }

        if (ecg.length > 0) {
            html += `<div class="shell-header" style="margin-top:1.5rem;margin-bottom:0.5rem;">
                 <span class="label-heading">ECG Test Reports</span>
               </div>`;
            html += ecg.map(r => {
                const meta = safeParseJson(r.ecg_meta);
                const isNorm = (r.result_status || '').toLowerCase() === 'normal';
                const color = ECG_CLASS_COLORS[r.result_status] || '#8686AC';
                return `
          <div class="summary-card" style="margin-bottom:1rem;border-left:5px solid ${color};">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
              <h4 style="color:#0A0A23;">
                ECG — <span style="color:${color};">${r.result_status}</span>
              </h4>
              <span class="ecg-status-badge ${isNorm ? 'normal' : 'abnormal'}">
                ${isNorm ? 'Normal' : 'Abnormal'}
              </span>
            </div>
            ${meta ? `
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-top:10px;">
              <div style="background:#F1F5F9;padding:8px;border-radius:8px;">
                <strong style="font-size:0.72rem;color:#64748B;text-transform:uppercase;">Avg Probability</strong>
                <p style="font-weight:800;color:#0A0A23;">${meta.avg_prob || '—'}%</p>
              </div>
              <div style="background:#F1F5F9;padding:8px;border-radius:8px;">
                <strong style="font-size:0.72rem;color:#64748B;text-transform:uppercase;">Segments</strong>
                <p style="font-weight:800;color:#0A0A23;">${meta.total_segments || '—'}</p>
              </div>
              <div style="background:#F1F5F9;padding:8px;border-radius:8px;">
                <strong style="font-size:0.72rem;color:#64748B;text-transform:uppercase;">Normal / Abnormal</strong>
                <p style="font-weight:800;color:#0A0A23;">
                  ${meta.normal_segments || 0} / ${meta.abnormal_segments || 0}
                </p>
              </div>
              <div style="background:#F1F5F9;padding:8px;border-radius:8px;">
                <strong style="font-size:0.72rem;color:#64748B;text-transform:uppercase;">Duration</strong>
                <p style="font-weight:800;color:#0A0A23;">${meta.duration || '—'}s</p>
              </div>
            </div>` : ''}
            <p style="font-size:0.7rem;margin-top:8px;color:#64748B;">
              File: ${r.ecg_filename || '—'} &nbsp;|&nbsp;
              Date: ${new Date(r.created_at).toLocaleString()}
            </p>
          </div>
        `;
            }).join('');
        }

        if (html === '') {
            html = '<p style="color:#94a3b8;text-align:center;padding:2rem;">No reports yet.</p>';
        }

        reportList.innerHTML = html;

    } catch (err) { console.error("Reports loading failed", err); }
}

// ─────────────────────────────────────────────────────────────
// AI PREDICTOR HANDLER
// ─────────────────────────────────────────────────────────────
async function handlePredict(e) {
    e.preventDefault();
    const userId = localStorage.getItem('userId');
    if (!userId) return alert("Please log in first.");

    const inputData = {
        user_id: userId,
        temperature: parseFloat(document.getElementById('temperature').value),
        heart_rate: parseFloat(document.getElementById('heart_rate').value),
        bp_sys: parseFloat(document.getElementById('bp_sys').value),
        bp_dia: parseFloat(document.getElementById('bp_dia').value),
        humidity: parseFloat(document.getElementById('humidity').value),
        fever: parseInt(document.getElementById('fever').value),
        cough: parseInt(document.getElementById('cough').value),
        chest_pain: parseInt(document.getElementById('chest_pain').value),
        shortness_breath: parseInt(document.getElementById('shortness_breath').value),
        fatigue: parseInt(document.getElementById('fatigue').value),
        headache: parseInt(document.getElementById('headache').value),
    };

    try {
        const res = await fetch('https://ecg-4ggp.onrender.com/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inputData),
        });
        const result = await res.json();
        if (res.ok) {
            document.getElementById('predictionResult').classList.remove('hidden');
            document.getElementById('predDisease').innerText = result.prediction;
            document.getElementById('predScore').innerText = result.score;
            document.getElementById('predDrugs').innerText = result.drugs;
            document.getElementById('predFoods').innerText = result.foods;
            document.getElementById('predRoutine').innerText = result.routine;
            loadReports();
            loadPatientOverview();
            loadPatientHealthTrend();
        } else {
            alert("Prediction failed: " + result.detail);
        }
    } catch (err) {
        console.error(err);
        alert("Network error.");
    }
}

// ─────────────────────────────────────────────────────────────
// DOCTOR: LOAD ALL PATIENTS
// ─────────────────────────────────────────────────────────────
async function loadAllPatients(side) {
    try {
        const res = await fetch('https://ecg-4ggp.onrender.com/api/search-patient?q=');
        const list = await res.json();
        document.getElementById(`list${side}`).innerHTML = list.map(p => `
      <div class="registry-item"
           onclick="selectPatient('${side}','${p.id_str}','${p.name}')">
        <strong>${p.name}</strong><br><small>${p.id_str}</small>
      </div>
    `).join('');
    } catch (err) { console.error(err); }
}

// ─────────────────────────────────────────────────────────────
// DOCTOR: SELECT PATIENT & RENDER CHARTS
// ─────────────────────────────────────────────────────────────
async function selectPatient(side, id_str, name) {
    document.getElementById(`data${side}`).classList.remove('hidden');
    document.getElementById(`name${side}`).innerText = `${name} // ID: ${id_str}`;
    document.getElementById(`list${side}`).innerHTML = "";

    try {
        const response = await fetch(`https://ecg-4ggp.onrender.com/api/reports/${id_str}`);
        const data = await response.json();

        if (data.length > 0) {
            const regular = data.filter(r => r.report_type !== 'ecg');
            const ecg = data.filter(r => r.report_type === 'ecg');

            if (regular.length > 0) {
                renderPatientCharts(side, regular);
                document.getElementById(`history${side}`).innerHTML = regular.map(r => `
          <div style="font-size:0.75rem;border-bottom:1px solid #EEE;padding:5px 0;">
            <strong>${r.result_status}</strong>
            (${new Date(r.created_at).toLocaleDateString()})<br>
            <small>Meds: ${r.suggested_drugs}</small><br>
            <small>Food: ${r.suggested_foods}</small>
          </div>
        `).join('');
            }

            // ECG history for doctor panel
            const ecgEl = document.getElementById(`ecgHistory${side}`);
            if (ecgEl) {
                if (ecg.length > 0) {
                    ecgEl.innerHTML = ecg.map(r => {
                        const meta = safeParseJson(r.ecg_meta);
                        const isNorm = (r.result_status || '').toLowerCase() === 'normal';
                        const color = ECG_CLASS_COLORS[r.result_status] || '#8686AC';
                        return `
              <div class="ecg-doctor-report-item">
                <strong style="color:${color};">${r.result_status}</strong>
                <span class="ecg-dr-badge ${isNorm ? 'normal' : 'abnormal'}">
                  ${isNorm ? 'Normal' : 'Abnormal'}
                </span><br>
                ${meta ? `<small>Segments: ${meta.total_segments || '—'} &nbsp;|&nbsp;
                  Normal: ${meta.normal_segments || 0} &nbsp;|&nbsp;
                  Abnormal: ${meta.abnormal_segments || 0} &nbsp;|&nbsp;
                  Avg Prob: ${meta.avg_prob || '—'}%</small><br>` : ''}
                <small style="color:#94a3b8;">
                  File: ${r.ecg_filename || '—'} &nbsp;|&nbsp;
                  ${new Date(r.created_at).toLocaleDateString()}
                </small>
              </div>
            `;
                    }).join('');
                } else {
                    ecgEl.innerHTML = '<p style="color:#94a3b8;font-size:0.85rem;padding:8px 0;">No ECG reports yet.</p>';
                }
            }
        }
    } catch (err) { console.error("Vital loading failed", err); }
}

function renderPatientCharts(side, data) {
    const labels = data.slice(0, 5).reverse().map((_, i) => `T-${i}`);

    new Chart(document.getElementById(`chart${side}_temp`), {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Temp °C',
                data: data.slice(0, 5).reverse().map(r => r.temperature),
                borderColor: '#FF6B6B',
            }],
        },
    });

    new Chart(document.getElementById(`chart${side}_bp`), {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: 'SYS', data: data.slice(0, 5).reverse().map(r => r.bp_sys), borderColor: '#4ECDC4' },
                { label: 'DIA', data: data.slice(0, 5).reverse().map(r => r.bp_dia), borderColor: '#45B7D1' },
            ],
        },
    });

    new Chart(document.getElementById(`chart${side}_hr`), {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'BPM',
                data: data.slice(0, 5).reverse().map(r => r.heart_rate),
                borderColor: '#8686AC',
            }],
        },
    });

    const symptomNames = ['Fever', 'Cough', 'Chest Pain', 'SOB', 'Fatigue', 'Headache'];
    const counts = [0, 0, 0, 0, 0, 0];
    data.forEach(r => {
        if (r.fever > 0) counts[0]++;
        if (r.cough > 0) counts[1]++;
        if (r.chest_pain > 0) counts[2]++;
        if (r.shortness_breath > 0) counts[3]++;
        if (r.fatigue > 0) counts[4]++;
        if (r.headache > 0) counts[5]++;
    });

    new Chart(document.getElementById(`chart${side}_symptoms`), {
        type: 'bar',
        data: {
            labels: symptomNames,
            datasets: [{
                label: 'Visits with symptom',
                data: counts,
                backgroundColor: '#8686AC',
            }],
        },
    });
}

// ─────────────────────────────────────────────────────────────
// DOCTOR: LIVE SEARCH
// ─────────────────────────────────────────────────────────────
async function liveSearch(side) {
    const q = document.getElementById(`input${side}`).value;
    if (q.length < 2) { loadAllPatients(side); return; }
    try {
        const res = await fetch(`https://ecg-4ggp.onrender.com/api/search-patient?q=${q}`);
        const list = await res.json();
        document.getElementById(`list${side}`).innerHTML = list.map(p => `
      <div class="registry-item"
           onclick="selectPatient('${side}','${p.id_str}','${p.name}')">
        <strong>${p.name}</strong><br><small>${p.id_str}</small>
      </div>
    `).join('');
    } catch (err) { console.error(err); }
}

// ─────────────────────────────────────────────────────────────
// DOCTOR: SEND MESSAGE
// ─────────────────────────────────────────────────────────────
async function sendAdvice(side) {
    const pId = document.getElementById(`name${side}`).innerText.split('ID: ')[1];
    const msg = document.getElementById(`msg${side}`).value;
    if (!msg) return alert("Please type a message.");

    try {
        const response = await fetch('https://ecg-4ggp.onrender.com/api/send-feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doctor_id: localStorage.getItem('userId'),
                patient_id: pId,
                message: msg,
            }),
        });
        if (response.ok) {
            alert("Message sent to patient.");
            document.getElementById(`msg${side}`).value = "";
            loadDoctorOverview();
        }
    } catch (err) { alert("Sending failed."); }
}

// ─────────────────────────────────────────────────────────────
// PATIENT HEALTH TREND CHART
// ─────────────────────────────────────────────────────────────
async function loadPatientHealthTrend() {
    const patientId = localStorage.getItem('userId');
    try {
        const res = await fetch(`https://ecg-4ggp.onrender.com/api/reports/${patientId}`);
        const reports = await res.json();
        const regular = reports.filter(r => r.report_type !== 'ecg');
        const recent = regular.slice(0, 7).reverse();
        new Chart(document.getElementById('healthChart'), {
            type: 'line',
            data: {
                labels: recent.map((_, i) => `Visit ${i + 1}`),
                datasets: [{
                    label: 'Risk %',
                    data: recent.map(r => r.analysis_score),
                    borderColor: '#8686AC',
                    backgroundColor: 'rgba(134,134,172,0.1)',
                }],
            },
        });
    } catch (err) { console.error(err); }
}

// ─────────────────────────────────────────────────────────────
// CHATBOT
// ─────────────────────────────────────────────────────────────
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    const userId = localStorage.getItem('userId');
    if (!userId) { alert("You must be logged in to use the Medical Assistant."); return; }

    const chatMessages = document.getElementById('chatMessages');

    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'message user';
    userMsgDiv.innerHTML = `<p>${escapeHtml(message)}</p>`;
    chatMessages.appendChild(userMsgDiv);
    input.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `<p>...</p>`;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('https://ecg-4ggp.onrender.com/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, message }),
        });

        document.getElementById('typingIndicator')?.remove();

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const data = await response.json();
        const botReply = data.reply || "Sorry, I couldn't process that.";

        const botMsgDiv = document.createElement('div');
        botMsgDiv.className = 'message bot';
        botMsgDiv.innerHTML = `<p>${escapeHtml(botReply)}</p>`;
        chatMessages.appendChild(botMsgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        console.error('Chatbot error:', error);
        document.getElementById('typingIndicator')?.remove();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot';
        errorDiv.innerHTML = `<p>Sorry, I'm having trouble connecting. Please try again later.</p>`;
        chatMessages.appendChild(errorDiv);
    }
}

function escapeHtml(unsafe) {
    return unsafe.replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}

// ═════════════════════════════════════════════════════════════
// ECG TEST — FILE HANDLING
// ═════════════════════════════════════════════════════════════

function ecgDragOver(e) {
    e.preventDefault();
    document.getElementById('ecgDropzone').classList.add('drag-over');
}

function ecgDragLeave(e) {
    document.getElementById('ecgDropzone').classList.remove('drag-over');
}

function ecgDrop(e) {
    e.preventDefault();
    document.getElementById('ecgDropzone').classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files && files.length > 0) processEcgFile(files[0]);
}

function handleEcgFileSelect(event) {
    const file = event.target.files[0];
    if (file) processEcgFile(file);
}

function processEcgFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['csv', 'txt'].includes(ext)) {
        alert('Unsupported file type. Please upload a .csv or .txt file.');
        return;
    }

    ecgSelectedFile = file;

    document.getElementById('ecgFileName').innerText = file.name;
    document.getElementById('ecgFileSize').innerText = formatBytes(file.size);
    document.getElementById('ecgFileInfo').classList.remove('hidden');
    document.getElementById('ecgAnalyzeBtn').classList.remove('hidden');

    // Show the recording start time input
    document.getElementById('ecgTimeInputArea').classList.remove('hidden');

    // Reset previous state
    document.getElementById('ecgSignalCard').classList.add('hidden');
    document.getElementById('ecgResultCard').classList.add('hidden');
    document.getElementById('ecgSaveConfirm').classList.add('hidden');
    document.getElementById('ecgStatusBar').classList.add('hidden');

    ecgRawData = null;
    ecgAnalysisResult = null;

    // Immediately parse and show waveform preview
    readEcgFileAndPreview(file);
}

function clearEcgFile() {
    ecgSelectedFile = null;
    ecgRawData = null;
    ecgAnalysisResult = null;

    document.getElementById('ecgFileInput').value = '';
    document.getElementById('ecgFileInfo').classList.add('hidden');
    document.getElementById('ecgAnalyzeBtn').classList.add('hidden');
    document.getElementById('ecgSignalCard').classList.add('hidden');
    document.getElementById('ecgResultCard').classList.add('hidden');
    document.getElementById('ecgStatusBar').classList.add('hidden');
    document.getElementById('ecgSaveConfirm').classList.add('hidden');
    document.getElementById('ecgTimeInputArea').classList.add('hidden');

    destroyChart('ecgWaveformChart');
    destroyChart('ecgProbChart');
    destroyChart('ecgConfChart');
    destroyChart('ecgSegChart1');
    destroyChart('ecgSegChart2');
}

// ─────────────────────────────────────────────────────────────
// ECG TEST — READ FILE & PREVIEW WAVEFORM
// ─────────────────────────────────────────────────────────────
function readEcgFileAndPreview(file) {
    setEcgStatus('Reading file...', true);

    const reader = new FileReader();
    reader.onload = function (e) {
        try {
            const raw = e.target.result;
            const tokens = raw.replace(/,/g, ' ').replace(/\t/g, ' ').split(/\s+/);
            const values = [];
            for (const tok of tokens) {
                const v = parseFloat(tok);
                if (!isNaN(v) && isFinite(v)) values.push(v);
            }

            if (values.length === 0) {
                setEcgStatus('No numeric values found in the file.', false);
                return;
            }
            if (values.length < ECG_WINDOW_SIZE) {
                setEcgStatus(
                    `Signal too short. Need ≥ ${ECG_WINDOW_SIZE} samples (10s at 360 Hz). Found ${values.length}.`,
                    false
                );
                return;
            }

            ecgRawData = new Float64Array(values);
            hideEcgStatus();
            renderEcgWaveform(ecgRawData, file.name);
            // Render two random 10-second segments for visual inspection
            renderRandomSegmentGraphs(ecgRawData);

        } catch (err) {
            setEcgStatus('Error reading file: ' + err.message, false);
        }
    };
    reader.onerror = () => setEcgStatus('Failed to read file.', false);
    reader.readAsText(file);
}

function renderEcgWaveform(data, filename) {
    const numSegments = Math.floor(data.length / ECG_WINDOW_SIZE);
    const totalSec = data.length / ECG_SAMPLING_RATE;

    document.getElementById('ecgStatSamples').innerText = data.length.toLocaleString();
    document.getElementById('ecgStatDuration').innerText = `${totalSec.toFixed(1)}s`;
    document.getElementById('ecgStatSegments').innerText = numSegments;
    document.getElementById('ecgStatSR').innerText = `${ECG_SAMPLING_RATE} Hz`;
    document.getElementById('ecgSignalTitle').innerText = `ECG Waveform — ${filename}`;

    // Downsample to 3000 points for smooth rendering
    const ds = downsampleArray(Array.from(data), 3000);
    const timeX = ds.map((_, i) => ((i / 3000) * totalSec).toFixed(2));

    destroyChart('ecgWaveformChart');

    const ctx = document.getElementById('ecgWaveformChart').getContext('2d');
    ecgWaveformChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeX,
            datasets: [{
                label: 'Amplitude',
                data: ds,
                borderColor: '#58a6ff',
                borderWidth: 1.2,
                pointRadius: 0,
                tension: 0.1,
                backgroundColor: 'rgba(88,166,255,0.04)',
                fill: true,
            }],
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: { title: items => `Time: ${items[0].label}s` },
                },
            },
            scales: {
                x: {
                    ticks: {
                        color: '#8b949e',
                        maxTicksLimit: 10,
                        font: { size: 9, family: 'monospace' },
                    },
                    grid: { color: '#21262d' },
                    title: {
                        display: true,
                        text: 'Time (s)',
                        color: '#8b949e',
                        font: { size: 10, family: 'monospace' },
                    },
                },
                y: {
                    ticks: { color: '#8b949e', font: { size: 9, family: 'monospace' } },
                    grid: { color: '#21262d' },
                    title: {
                        display: true,
                        text: 'Amplitude',
                        color: '#8b949e',
                        font: { size: 10, family: 'monospace' },
                    },
                },
            },
        },
    });

    document.getElementById('ecgSignalCard').classList.remove('hidden');
}

// ─────────────────────────────────────────────────────────────
// ECG TEST — ANALYZE (sends file to backend)
// ─────────────────────────────────────────────────────────────
async function analyzeEcg() {
    if (!ecgSelectedFile) { alert('Please select a file first.'); return; }

    const btn = document.getElementById('ecgAnalyzeBtn');
    btn.disabled = true;
    btn.innerText = '⏳ Analyzing...';

    setEcgStatus('Uploading ECG file to AI backend...', true);
    document.getElementById('ecgResultCard').classList.add('hidden');
    document.getElementById('ecgSaveConfirm').classList.add('hidden');

    try {
        const formData = new FormData();
        formData.append('file', ecgSelectedFile);
        formData.append('user_id', localStorage.getItem('userId') || '');

        // Capture the recording start time (if any)
        const startTimeInput = document.getElementById('ecgStartTime');
        if (startTimeInput && startTimeInput.value) {
            ecgStartTimeValue = startTimeInput.value; // store ISO string
            formData.append('start_time', ecgStartTimeValue);
        } else {
            ecgStartTimeValue = null;
        }

        setEcgStatus('Running ensemble model prediction (ResNet + Inception + Transformer)...', true);

        const res = await fetch('https://ecg-4ggp.onrender.com/api/ecg-predict', {
            method: 'POST',
            body: formData,
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const result = await res.json();
        ecgAnalysisResult = result;

        hideEcgStatus();
        renderEcgResults(result);

    } catch (err) {
        console.error('ECG analysis error:', err);
        setEcgStatus(`Analysis failed: ${err.message}`, false);
    } finally {
        btn.disabled = false;
        btn.innerText = '⚡ Analyze ECG Signal';
    }
}

// ─────────────────────────────────────────────────────────────
// ECG TEST — RENDER RESULTS
// ─────────────────────────────────────────────────────────────
function renderEcgResults(result) {
    /*
      Expected result shape from backend /api/ecg-predict:
      {
        top_condition:  string,
        top_prob:       float (0–100),
        normal_count:   int,
        abnormal_count: int,
        total_segments: int,
        class_probs:    { [className]: float (0–100) },
        segments:       [{ seg, start_t, end_t, prediction, confidence }]
      }
    */

    const isNorm = result.top_condition === 'Normal';

    // ── Verdict banner ────────────────────────────────────────
    const banner = document.getElementById('ecgVerdictBanner');
    banner.className = 'ecg-verdict-banner ' +
        (isNorm ? 'condition-normal'
            : result.top_prob > 60 ? 'condition-abnormal' : 'condition-warning');

    document.getElementById('ecgVerdictCondition').innerText =
        result.top_condition.toUpperCase();
    document.getElementById('ecgVerdictProb').innerText =
        `${parseFloat(result.top_prob).toFixed(1)}%`;
    document.getElementById('ecgVerdictNormal').innerText =
        `${result.normal_count} / ${result.total_segments}`;
    document.getElementById('ecgVerdictAbnormal').innerText =
        `${result.abnormal_count} / ${result.total_segments}`;

    // ── Probability bar chart ─────────────────────────────────
    const classProbs = result.class_probs || {};
    const sortedNames = Object.keys(classProbs).sort((a, b) => classProbs[b] - classProbs[a]);
    const sortedVals = sortedNames.map(n => parseFloat(classProbs[n]).toFixed(1));
    const barColors = sortedNames.map(n => ECG_CLASS_COLORS[n] || '#8686AC');

    destroyChart('ecgProbChart');
    const probCtx = document.getElementById('ecgProbChart').getContext('2d');
    ecgProbChart = new Chart(probCtx, {
        type: 'bar',
        data: {
            labels: sortedNames,
            datasets: [{
                label: 'Avg Probability (%)',
                data: sortedVals,
                backgroundColor: barColors.map(c => c + 'CC'),
                borderColor: barColors,
                borderWidth: 1.5,
                borderRadius: 6,
            }],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    min: 0, max: 100,
                    ticks: { callback: v => v + '%', color: '#475569', font: { size: 10 } },
                    grid: { color: '#e2e8f0' },
                },
                y: {
                    ticks: { color: '#1e293b', font: { size: 11, weight: '700' } },
                    grid: { display: false },
                },
            },
        },
    });

    // ── Confidence over time chart ────────────────────────────
    const segs = result.segments || [];
    const confTimes = segs.map(s => s.start_t);
    const confVals = segs.map(s => (s.confidence * 100).toFixed(1));
    const dotColors = segs.map(s => ECG_CLASS_COLORS[s.prediction] || '#8686AC');

    destroyChart('ecgConfChart');
    const confCtx = document.getElementById('ecgConfChart').getContext('2d');
    ecgConfChart = new Chart(confCtx, {
        type: 'line',
        data: {
            labels: confTimes,
            datasets: [{
                label: 'Confidence (%)',
                data: confVals,
                borderColor: '#8b949e',
                borderWidth: 1.2,
                pointBackgroundColor: dotColors,
                pointBorderColor: '#f1f5f9',
                pointBorderWidth: 1.5,
                pointRadius: 5,
                tension: 0.3,
                fill: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    ticks: {
                        callback: (_, i) => `${confTimes[i]}s`,
                        color: '#475569',
                        font: { size: 9 },
                        maxTicksLimit: 12,
                    },
                    grid: { color: '#e2e8f0' },
                    title: { display: true, text: 'Time (s)', color: '#475569', font: { size: 10 } },
                },
                y: {
                    min: 0, max: 100,
                    ticks: { callback: v => v + '%', color: '#475569', font: { size: 10 } },
                    grid: { color: '#e2e8f0' },
                },
            },
        },
    });

    // ── Segment table with clock times ─────────────────────────
    const hasStartTime = !!ecgStartTimeValue;
    const timeHeader = document.getElementById('ecgTableTimeHeader');
    if (timeHeader) {
        timeHeader.style.display = hasStartTime ? 'table-cell' : 'none';
    }

    const tbody = document.getElementById('ecgSegmentTableBody');
    tbody.innerHTML = segs.map((s, i) => {
        const isSegNorm = s.prediction === 'Normal';
        const color = ECG_CLASS_COLORS[s.prediction] || '#8686AC';
        let clockTimeCell = '';
        if (hasStartTime) {
            const clockTime = computeClockTime(s.start_t, ecgStartTimeValue);
            clockTimeCell = `<td class="${!isSegNorm ? 'ecg-clock-cell abnormal-time' : 'ecg-clock-cell'}">${clockTime || '—'}<\/td>`;
        } else {
            clockTimeCell = '<td>—<\/td>';
        }
        return `
      <tr>
        <td>#${i + 1}<\/td>
        <td>${parseFloat(s.start_t).toFixed(1)}<\/td>
        <td>${parseFloat(s.end_t).toFixed(1)}<\/td>
        ${clockTimeCell}
        <td>
            <span class="ecg-condition-pill"
                  style="background:${color}22;color:${color};">
                ${s.prediction}
            </span>
        <\/td>
        <td><strong>${(s.confidence * 100).toFixed(1)}%<\/strong><\/td>
        <td>
            <span class="ecg-status-badge ${isSegNorm ? 'normal' : 'abnormal'}">
                ${isSegNorm ? 'Normal' : 'Abnormal'}
            </span>
        <\/td>
      <\/tr>
    `;
    }).join('');

    // ── Abnormal time log ─────────────────────────────────────
    if (hasStartTime) {
        const abnormalIndices = [];
        segs.forEach((s, idx) => {
            if (s.prediction !== 'Normal') {
                abnormalIndices.push({ idx: idx + 1, seg: s });
            }
        });
        const abnormalLogDiv = document.getElementById('ecgAbnormalTimeLog');
        if (abnormalIndices.length > 0) {
            abnormalLogDiv.classList.remove('hidden');
            document.getElementById('ecgAbnormalIntro').innerText = `Detected ${abnormalIndices.length} abnormal segment(s) during your recording:`;
            document.getElementById('ecgAbnormalTimeBody').innerHTML = abnormalIndices.map(item => {
                const clockTime = computeClockTime(item.seg.start_t, ecgStartTimeValue);
                return `
            <div class="ecg-abnormal-item">
                <div class="abn-seg">Segment ${item.idx}</div>
                <div class="abn-condition">${item.seg.prediction}</div>
                <div class="abn-clock">${clockTime || 'Time unknown'}</div>
                <div class="abn-conf">Confidence: ${(item.seg.confidence * 100).toFixed(1)}%</div>
            </div>
            `;
            }).join('');
        } else {
            abnormalLogDiv.classList.add('hidden');
        }
    } else {
        document.getElementById('ecgAbnormalTimeLog').classList.add('hidden');
    }

    document.getElementById('ecgResultCard').classList.remove('hidden');
}

// ─────────────────────────────────────────────────────────────
// ECG TEST — SAVE REPORT TO MY REPORTS
// ─────────────────────────────────────────────────────────────
async function saveEcgReport() {
    if (!ecgAnalysisResult) { alert('No analysis result to save.'); return; }

    const userId = localStorage.getItem('userId');
    if (!userId) { alert('Please log in first.'); return; }

    const r = ecgAnalysisResult;

    const payload = {
        user_id: userId,
        report_type: 'ecg',
        result_status: r.top_condition,
        analysis_score: parseFloat(r.top_prob).toFixed(1),
        ecg_filename: ecgSelectedFile ? ecgSelectedFile.name : '—',
        ecg_meta: JSON.stringify({
            total_segments: r.total_segments,
            normal_segments: r.normal_count,
            abnormal_segments: r.abnormal_count,
            avg_prob: parseFloat(r.top_prob).toFixed(1),
            duration: r.total_segments * 10,
        }),
        suggested_drugs: '',
        suggested_foods: '',
        routine: '',
    };

    try {
        const res = await fetch('https://ecg-4ggp.onrender.com/api/save-ecg-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (res.ok) {
            document.getElementById('ecgSaveConfirm').classList.remove('hidden');
            loadReports(); // Refresh My Reports section in background
        } else {
            const err = await res.json().catch(() => ({ detail: 'Save failed' }));
            alert('Save failed: ' + (err.detail || 'Unknown error'));
        }
    } catch (err) {
        console.error('Save ECG report error:', err);
        alert('Network error while saving report.');
    }
}

// ═════════════════════════════════════════════════════════════
// SHARED HELPERS
// ═════════════════════════════════════════════════════════════

function setEcgStatus(text, pulse) {
    const bar = document.getElementById('ecgStatusBar');
    const dot = bar.querySelector('.ecg-status-pulse');
    document.getElementById('ecgStatusText').innerText = text;
    bar.classList.remove('hidden');
    dot.style.background = pulse ? '#8686ac' : '#e74c3c';
    dot.style.animation = pulse ? 'ecgPulse 1.1s ease-in-out infinite' : 'none';
}

function hideEcgStatus() {
    document.getElementById('ecgStatusBar').classList.add('hidden');
}

function destroyChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const existing = Chart.getChart(canvas);
    if (existing) existing.destroy();
}

function downsampleArray(arr, n) {
    if (arr.length <= n) return arr;
    const step = arr.length / n;
    const result = [];
    for (let i = 0; i < n; i++) {
        result.push(arr[Math.floor(i * step)]);
    }
    return result;
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(2) + ' MB';
}

function safeParseJson(str) {
    if (!str) return null;
    try { return JSON.parse(str); } catch { return null; }
}

// =============================================================
// ECG – Random Segment Graphs (Graph 2 & 3)
// =============================================================
function renderRandomSegmentGraphs(signal) {
    if (!signal || signal.length === 0) return;

    const totalSamples = signal.length;
    const windowSamples = ECG_WINDOW_SIZE; // 3600 samples = 10s
    const maxStartSample = totalSamples - windowSamples;
    if (maxStartSample <= 0) {
        // Not enough samples to create a 10s segment
        showSegmentPlaceholder('ecgSegChart1', 'Insufficient signal length for 10s segment.');
        showSegmentPlaceholder('ecgSegChart2', 'Insufficient signal length for 10s segment.');
        return;
    }

    // Generate two random start indices
    let start1 = Math.floor(Math.random() * (maxStartSample + 1));
    let start2 = Math.floor(Math.random() * (maxStartSample + 1));
    // Ensure the two segments are different (or at least not identical)
    while (start2 === start1 && maxStartSample > 0) {
        start2 = Math.floor(Math.random() * (maxStartSample + 1));
    }

    const end1 = start1 + windowSamples;
    const end2 = start2 + windowSamples;

    const seg1 = signal.slice(start1, end1);
    const seg2 = signal.slice(start2, end2);

    const startTime1 = (start1 / ECG_SAMPLING_RATE).toFixed(2);
    const startTime2 = (start2 / ECG_SAMPLING_RATE).toFixed(2);
    const endTime1 = (end1 / ECG_SAMPLING_RATE).toFixed(2);
    const endTime2 = (end2 / ECG_SAMPLING_RATE).toFixed(2);

    // Update labels in HTML
    document.getElementById('ecgSegLabel1').innerHTML = `Segment (${startTime1}s – ${endTime1}s)`;
    document.getElementById('ecgSegLabel2').innerHTML = `Segment (${startTime2}s – ${endTime2}s)`;

    // Render charts
    renderSegmentChart('ecgSegChart1', seg1, startTime1);
    renderSegmentChart('ecgSegChart2', seg2, startTime2);
}

function renderSegmentChart(canvasId, signalSegment, startTimeLabel) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Destroy existing Chart instance if any
    const existing = Chart.getChart(canvas);
    if (existing) existing.destroy();

    // Downsample for smoother rendering (keep about 1000 points per 10s)
    const targetPoints = 1000;
    let data = signalSegment;
    if (signalSegment.length > targetPoints) {
        data = downsampleArray(Array.from(signalSegment), targetPoints);
    }

    const timePoints = data.map((_, i) => ((i / data.length) * 10).toFixed(2)); // 0 to 10 seconds

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timePoints,
            datasets: [{
                label: 'Amplitude',
                data: data,
                borderColor: '#58a6ff',
                borderWidth: 1.2,
                pointRadius: 0,
                tension: 0.1,
                backgroundColor: 'rgba(88,166,255,0.04)',
                fill: true,
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: items => `Time: ${items[0].label}s (relative to start of segment)`
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#8b949e',
                        maxTicksLimit: 8,
                        font: { size: 9, family: 'monospace' }
                    },
                    grid: { color: '#21262d' },
                    title: {
                        display: true,
                        text: 'Time (s) within segment',
                        color: '#8b949e',
                        font: { size: 10, family: 'monospace' }
                    }
                },
                y: {
                    ticks: { color: '#8b949e', font: { size: 9, family: 'monospace' } },
                    grid: { color: '#21262d' },
                    title: {
                        display: true,
                        text: 'Amplitude',
                        color: '#8b949e',
                        font: { size: 10, family: 'monospace' }
                    }
                }
            }
        }
    });
}

function showSegmentPlaceholder(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const existing = Chart.getChart(canvas);
    if (existing) existing.destroy();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#8b949e';
    ctx.font = '12px monospace';
    ctx.fillText(message, 10, 30);
}

function computeClockTime(secondsFromStart, startISOString) {
    if (!startISOString) return null;
    const startDate = new Date(startISOString);
    if (isNaN(startDate)) return null;
    const segmentDate = new Date(startDate.getTime() + secondsFromStart * 1000);
    return segmentDate.toLocaleString(); // or format as needed
}

