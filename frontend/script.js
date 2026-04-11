const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {

    /* ═══════════════════════════════════════════════
       1. FOLDER DEPTH DETECTION
    ═══════════════════════════════════════════════ */
    const path = window.location.pathname;
    let baseRelPath = "";
    if (path.includes("/services/") || path.includes("/diseases/")) {
        baseRelPath = "../../";
    } else if (path.includes("/pages/")) {
        baseRelPath = "../";
    }

    /* ═══════════════════════════════════════════════
       2. DISEASE MEGA-MENU GENERATION
    ═══════════════════════════════════════════════ */
    const diseases = [
        "Asthma", "Alzheimer Disease", "Anemia", "Arthritis", "Bronchitis",
        "Cancer", "COVID-19", "Cholera", "Chronic Kidney Disease", "Dengue",
        "Diabetes", "Depression", "Epilepsy", "Gastritis", "Heart Attack",
        "Hepatitis B", "HIV AIDS", "Hypertension", "Hypotension", "Influenza",
        "Leukemia", "Liver Cirrhosis", "Malaria", "Migraine", "Obesity",
        "Pneumonia", "Psoriasis", "Stroke", "Tuberculosis", "Typhoid"
    ];
    const grid = document.getElementById("diseaseGrid");
    if (grid) {
        diseases.forEach(disease => {
            const link = document.createElement("a");
            const urlSafe = disease.toLowerCase().replace(/'/g, "-").replace(/\s+/g, "-");
            link.href = `${baseRelPath}pages/diseases/${urlSafe}.html`;
            link.textContent = disease;
            grid.appendChild(link);
        });
    }

    /* ═══════════════════════════════════════════════
       3. HAMBURGER MENU
    ═══════════════════════════════════════════════ */
    const hamburger = document.getElementById("hamburger");
    const navLinks = document.getElementById("navLinks");

    if (hamburger && navLinks) {
        hamburger.addEventListener("click", (e) => {
            e.stopPropagation();
            navLinks.classList.toggle("active");
            hamburger.classList.toggle("open");
        });
    }

    /* ═══════════════════════════════════════════════
       4. MOBILE DROPDOWN TOGGLE
    ═══════════════════════════════════════════════ */
    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach(item => {
        const sub = item.querySelector(".dropdown, .mega-menu");
        if (!sub) return;
        item.classList.add("has-sub");

        const topLink = item.querySelector(":scope > a");
        if (!topLink) return;

        topLink.addEventListener("click", (e) => {
            if (window.innerWidth > 768) return;
            e.preventDefault();
            e.stopPropagation();
            const isOpen = item.classList.contains("open");
            navItems.forEach(n => n.classList.remove("open"));
            if (!isOpen) item.classList.add("open");
        });
    });

    /* Close sidebar + dropdowns on outside tap */
    document.addEventListener("click", (e) => {
        if (window.innerWidth > 768) return;
        if (navLinks && hamburger &&
            !navLinks.contains(e.target) &&
            !hamburger.contains(e.target)) {
            navLinks.classList.remove("active");
            hamburger.classList.remove("open");
        }
        let inside = false;
        navItems.forEach(n => { if (n.contains(e.target)) inside = true; });
        if (!inside) navItems.forEach(n => n.classList.remove("open"));
    });

    /* ═══════════════════════════════════════════════
       5. AUTH MODAL
    ═══════════════════════════════════════════════ */
    const modal = document.getElementById("authModal");

    window.openAuthModal = function (startTab) {
        if (!modal) return;
        modal.style.display = "flex";
        window.switchTab(startTab || "auth");
    };

    function closeModal() {
        if (modal) modal.style.display = "none";
    }

    /* Initialize System button */
    const initBtn = document.getElementById("initSystemBtn");
    if (initBtn) {
        initBtn.addEventListener("click", () => window.openAuthModal("auth"));
    }

    /* Backdrop click */
    window.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
    });

    /* Cancel buttons */
    ["closeModalBtn", "closeRegBtn"].forEach(id => {
        const b = document.getElementById(id);
        if (b) b.addEventListener("click", closeModal);
    });

    /* ── Sign In → POST /api/login ── */
    const signInBtn = document.getElementById("signInBtn");
    if (signInBtn) {
        signInBtn.addEventListener("click", async () => {
            const user_id = (document.getElementById("loginId")?.value || "").trim();
            const password = (document.getElementById("loginPassword")?.value || "").trim();

            if (!user_id) { alert("Please enter your Institutional ID."); return; }
            if (!password) { alert("Please enter your Password."); return; }

            signInBtn.textContent = "Authenticating…";
            signInBtn.disabled = true;

            try {
                const res = await fetch(`${API_BASE}/api/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id, password })
                });

                if (res.status === 401) {
                    alert("Invalid credentials. Check your ID and password.");
                    return;
                }
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    alert(err.detail || "Login failed. Please try again.");
                    return;
                }

                const data = await res.json();
                localStorage.setItem("hb_current", JSON.stringify({
                    name: data.name,
                    id: data.user_id,
                    role: data.role
                }));
                localStorage.setItem("userName", data.name);
                localStorage.setItem("userId", data.user_id);
                localStorage.setItem("userRole", data.role);

                closeModal();
                window.location.href = "dashboard.html";

            } catch (err) {
                alert("Cannot reach server. Make sure the backend is running.");
                console.error(err);
            } finally {
                signInBtn.textContent = "Sign In";
                signInBtn.disabled = false;
            }
        });
    }

    /* ── Sign Up → POST /api/signup ── */
    const signUpBtn = document.getElementById("signUpBtn");
    if (signUpBtn) {
        signUpBtn.addEventListener("click", async () => {
            const user_id = (document.getElementById("regId")?.value || "").trim();
            const name = (document.getElementById("regName")?.value || "").trim();
            const email = (document.getElementById("regEmail")?.value || "").trim();
            const phone = (document.getElementById("regPhone")?.value || "").trim();
            const password = (document.getElementById("regPassword")?.value || "").trim();

            if (!user_id || !name || !password) {
                alert("Institutional ID, Full Name, and Password are required.");
                return;
            }
            if (!email && !phone) {
                alert("Please provide at least one contact: Email or Phone.");
                return;
            }

            const isPatient = document.getElementById("btnPatient")?.classList.contains("active");
            const role = isPatient ? "patient" : "staff";

            signUpBtn.textContent = "Registering…";
            signUpBtn.disabled = true;

            try {
                const res = await fetch(`${API_BASE}/api/signup`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id, name, email, phone, password, role })
                });

                if (res.status === 400) {
                    const err = await res.json().catch(() => ({}));
                    alert(err.detail || "This Institutional ID is already registered. Please sign in.");
                    window.switchTab("auth");
                    return;
                }
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    alert(err.detail || "Registration failed. Please try again.");
                    return;
                }

                alert(`Registration successful! Welcome, ${name}. Please sign in.`);
                window.switchTab("auth");

            } catch (err) {
                alert("Cannot reach server. Make sure the backend is running.");
                console.error(err);
            } finally {
                signUpBtn.textContent = "Sign Up";
                signUpBtn.disabled = false;
            }
        });
    }

    /* Restore session on page load */
    updateHeroUI();

    function updateHeroUI() {
        const current = JSON.parse(localStorage.getItem("hb_current") || "null");
        const btn = document.getElementById("initSystemBtn");
        if (!btn || !current?.name) return;

        const first = current.name.split(" ")[0];
        btn.textContent = `${first} — Dashboard`;
        btn.onclick = () => { window.location.href = "dashboard.html"; };

        const heroP = document.querySelector(".hero p");
        if (heroP && !heroP.dataset.updated) {
            heroP.textContent = `Active clinical session for ${current.name}. You can now access real-time diagnostics and history.`;
            heroP.dataset.updated = "1";
        }
    }

});

/* ═══════════════════════════════════════════════
   6. GLOBAL: Tab switcher
═══════════════════════════════════════════════ */
window.switchTab = function (tab) {
    const tabAuth = document.getElementById("tabAuth");
    const tabReg = document.getElementById("tabReg");
    const panelAuth = document.getElementById("panelAuth");
    const panelReg = document.getElementById("panelReg");
    if (!tabAuth || !tabReg || !panelAuth || !panelReg) return;

    if (tab === "reg") {
        tabReg.classList.add("active"); tabAuth.classList.remove("active");
        panelReg.classList.remove("hidden"); panelAuth.classList.add("hidden");
    } else {
        tabAuth.classList.add("active"); tabReg.classList.remove("active");
        panelAuth.classList.remove("hidden"); panelReg.classList.add("hidden");
    }
};

/* ═══════════════════════════════════════════════
   7. GLOBAL: Account type toggle
═══════════════════════════════════════════════ */
window.setAccountType = function (type) {
    const btnP = document.getElementById("btnPatient");
    const btnS = document.getElementById("btnStaff");
    const regId = document.getElementById("regId");
    if (type === "patient") {
        btnP?.classList.add("active"); btnS?.classList.remove("active");
        if (regId) regId.placeholder = "PAT-0000";
    } else {
        btnS?.classList.add("active"); btnP?.classList.remove("active");
        if (regId) regId.placeholder = "STF-0000";
    }
};

/* ═══════════════════════════════════════════════
   8. LEGACY: handleAuth (sub-page inline onclick)
═══════════════════════════════════════════════ */
window.handleAuth = function (mode) {
    const p = window.location.pathname;
    let authPath = "auth.html";
    if (p.includes("/services/") || p.includes("/diseases/")) authPath = "../../auth.html";
    else if (p.includes("/pages/")) authPath = "../auth.html";
    window.location.href = `${authPath}?mode=${mode}`;
};