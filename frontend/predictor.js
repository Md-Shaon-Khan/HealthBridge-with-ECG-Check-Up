// AI HEALTH PREDICTOR - Full Clinical Advice Integration

document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userId = localStorage.getItem('userId');
    if (!userId) {
        alert("Please sign in first to use the prediction service.");
        window.location.href = "auth.html?mode=signin";
        return;
    }

    const formData = {
        user_id: userId,
        temperature: parseFloat(document.getElementById('temp').value),
        heart_rate: parseFloat(document.getElementById('heart_rate').value),
        bp_dia: parseFloat(document.getElementById('bp_dia').value),
        bp_sys: parseFloat(document.getElementById('bp_sys').value),
        humidity: parseFloat(document.getElementById('humidity').value),
        fever: document.getElementById('fever').checked ? 1 : 0,
        cough: document.getElementById('cough').checked ? 1 : 0,
        chest_pain: document.getElementById('chest_pain').checked ? 1 : 0,
        shortness_breath: document.getElementById('shortness_breath').checked ? 1 : 0,
        fatigue: document.getElementById('fatigue').checked ? 1 : 0,
        headache: document.getElementById('headache').checked ? 1 : 0
    };

    console.log("Submitting prediction data:", formData);

    try {
        const response = await fetch('https://api.ecg-iit-ju-shaon.xyz/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            // Update result box with disease and score
            document.getElementById('predictionResult').innerHTML = `<strong>Predicted Condition:</strong> ${result.prediction}`;
            document.getElementById('predictionScore').innerHTML = `<strong>Health Score:</strong> ${result.score}%`;

            // Display clinical advice
            const adviceHtml = `
        <div class="advice-section">
          <h4>📋 Suggested Drugs</h4>
          <p>${result.drugs}</p>
          <h4>🥗 Recommended Foods</h4>
          <p>${result.foods}</p>
          <h4>🩺 Clinical Routine</h4>
          <p>${result.routine}</p>
        </div>
      `;
            const adviceContainer = document.getElementById('clinicalAdvice');
            if (adviceContainer) adviceContainer.innerHTML = adviceHtml;

            // Show result box and scroll
            const resultBox = document.getElementById('resultBox');
            if (resultBox) {
                resultBox.style.display = 'block';
                window.scrollTo({ top: resultBox.offsetTop - 20, behavior: 'smooth' });
            }
        } else {
            alert("Prediction error: " + (result.detail || "Unknown server error"));
        }
    } catch (err) {
        console.error(err);
        alert("Cannot reach the prediction server. Make sure FastAPI is running at https://api.ecg-iit-ju-shaon.xyz");
    }
});