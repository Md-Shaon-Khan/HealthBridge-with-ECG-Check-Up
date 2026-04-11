document.addEventListener("DOMContentLoaded", () => {
  // Determine base path for links (works in root, /pages/, /pages/services/, etc.)
  const path = window.location.pathname;
  let basePath = "";
  if (path.includes("/services/") || path.includes("/diseases/")) {
    basePath = "../../";
  } else if (path.includes("/pages/")) {
    basePath = "../";
  } else {
    basePath = "";
  }

  const navHTML = `
    <nav class="navbar">
      <div class="logo" onclick="location.href='${basePath}index.html'">
        <span class="logo-hb">HB</span> Health<span>Bridge</span>
      </div>
      <div class="hamburger" id="hamburger">
        <span></span><span></span><span></span>
      </div>
      <ul class="nav-links" id="navLinks">
        <li class="nav-item mega-dropdown">
          <a href="#">Disease</a>
          <div class="mega-menu">
            <div class="mega-menu-content">
              <h3 class="menu-title">Medical Conditions and Diseases</h3>
              <div class="mega-menu-grid" id="diseaseGrid"></div>
            </div>
          </div>
        </li>
        <li class="nav-item">
          <a href="#">Services</a>
          <div class="dropdown">
            <a href="${basePath}pages/services/heart-risk.html">Heart Risk</a>
            <a href="${basePath}pages/services/fever.html">Fever Respiratory</a>
            <a href="${basePath}pages/services/hypertension.html">Hypertension</a>
            <a href="${basePath}pages/services/hypotension.html">Hypotension</a>
            <a href="${basePath}pages/services/normal.html">General Checkup</a>
          </div>
        </li>
        <li class="nav-item"><a href="${basePath}pages/wellness.html">Wellness</a></li>
        <li class="nav-item"><a href="${basePath}pages/primary-drugs.html">Primary Drugs</a></li>
        <li class="nav-item"><a href="${basePath}pages/foods.html">Foods</a></li>
        <li class="nav-item"><a href="${basePath}pages/contact.html">Contact</a></li>
      </ul>
      <div class="nav-auth">
        <button class="btn btn-login" onclick="handleAuth('signin')">Sign In</button>
        <button class="btn btn-signup" onclick="handleAuth('signup')">Sign Up</button>
      </div>
    </nav>
  `;

  document.body.insertAdjacentHTML('afterbegin', navHTML);

  // --- Disease Mega Menu (30 diseases) ---
  const diseases = [
    "Asthma", "Alzheimer Disease", "Anemia", "Arthritis", "Bronchitis",
    "Cancer", "COVID-19", "Cholera", "Chronic Kidney Disease", "Dengue",
    "Diabetes", "Depression", "Epilepsy", "Gastritis", "Heart Attack",
    "Hepatitis B", "HIV AIDS", "Hypertension", "Hypotension", "Influenza",
    "Leukemia", "Liver Cirrhosis", "Malaria", "Migraine", "Obesity",
    "Pneumonia", "Psoriasis", "Stroke", "Tuberculosis", "Typhoid"
  ];
  const grid = document.getElementById('diseaseGrid');
  if (grid) {
    diseases.forEach(disease => {
      const link = document.createElement('a');
      const urlSafeName = disease.toLowerCase().replace(/'/g, '-').replace(/\s+/g, '-');
      link.href = `${basePath}pages/diseases/${urlSafeName}.html`;
      link.textContent = disease;
      grid.appendChild(link);
    });
  }

  // --- Hamburger menu (mobile) ---
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      navLinks.classList.toggle('active');
    });
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 && navLinks.classList.contains('active') &&
        !navLinks.contains(e.target) && !hamburger.contains(e.target)) {
        navLinks.classList.remove('active');
      }
    });
  }

  // --- TOUCH‑FRIENDLY DROPDOWNS (works on phones & tablets) ---
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    const dropdown = item.querySelector('.dropdown, .mega-menu');
    if (dropdown) {
      const link = item.querySelector('> a');
      link.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
          e.preventDefault();        // stop navigation, just open menu
          // Close all other open menus
          navItems.forEach(nav => {
            if (nav !== item) nav.classList.remove('open');
          });
          item.classList.toggle('open');
        }
      });
    }
  });

  // Close dropdowns when clicking outside (on touch devices)
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
      let insideNav = false;
      navItems.forEach(nav => {
        if (nav.contains(e.target)) insideNav = true;
      });
      if (!insideNav && !hamburger?.contains(e.target)) {
        navItems.forEach(nav => nav.classList.remove('open'));
      }
    }
  });
});

// Global auth handler
function handleAuth(mode) {
  const path = window.location.pathname;
  let authPath = "auth.html";
  if (path.includes("/services/") || path.includes("/diseases/")) {
    authPath = "../../auth.html";
  } else if (path.includes("/pages/")) {
    authPath = "../auth.html";
  }
  window.location.href = `${authPath}?mode=${mode}`;
}