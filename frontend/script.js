// 🌾 Crop Recommendation Form
const form = document.getElementById("cropForm");
const resultDiv = document.getElementById("result");

// Session check – check if user is authenticated via backend
async function checkAuthentication() {
  try {
    const response = await fetch("http://127.0.0.1:8000/auth/me", {
      credentials: "include"  // Include cookies
    });
    
    if (response.ok) {
      const data = await response.json();
      document.getElementById("userSpan").textContent = data.username;
    } else {
      // Not authenticated, redirect to login
      window.location.href = "login.html";
    }
  } catch (error) {
    // Error checking auth, redirect to login
    console.error("Auth check failed:", error);
    window.location.href = "login.html";
  }
}

// Run authentication check
checkAuthentication();

// Check for saved dark mode preference
if (localStorage.getItem("darkMode") === "true") {
  document.body.classList.add("dark-mode");
}

form.addEventListener("submit", async function (event) {
  event.preventDefault();

  const soilTypeEl = document.getElementById("soilType");
  const cityEl = document.getElementById("city");
  const seasonEl = document.getElementById("season");

  if (soilTypeEl && cityEl && seasonEl) {
    const soilType = soilTypeEl.value.trim();
    const city = cityEl.value.trim();
    const season = seasonEl.value.trim();

    if (!soilType || !city || !season) {
      alert("⚠️ Please fill in Soil Type, City and Season.");
      return;
    }

    const url = `http://127.0.0.1:8000/recommend_crop_auto/${soilType}/${city}/${season}`;

    try {
      const response = await fetch(url, {
        credentials: "include"  // Include cookies for authentication
      });
      const data = await response.json();

      if (data.recommended_crops) {
        resultDiv.innerHTML = `
          🌍 <strong>Location:</strong> ${data.location}<br/>
          🧪 <strong>Soil Type:</strong> ${data.soil_type}<br/>
          🕒 <strong>Season:</strong> ${data.season}<br/>
          🌡️ <strong>Temp:</strong> ${data.temperature}°C<br/>
          💧 <strong>Humidity:</strong> ${data.humidity}%<br/>
          🌾 <strong>Recommended Crops:</strong> 
          <span style="color:green">${data.recommended_crops.join(", ")}</span>
        `;
        speak(`Recommended crop is ${data.recommended_crops[0]}`);
      } else {
        resultDiv.textContent = data.error || "No crops found.";
      }
    } catch (error) {
      console.error("Error:", error);
      resultDiv.textContent = "❌ Error in auto prediction.";
    }
  }
});

// 🔊 Text-to-Speech
function speak(text, lang = "en-IN") {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  speechSynthesis.speak(utterance);
}

// 🌙 Dark Mode Toggle
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  
  // Save preference to localStorage
  const isDarkMode = document.body.classList.contains("dark-mode");
  localStorage.setItem("darkMode", isDarkMode);
}

// 🎤 Voice Input
function startVoiceInput(fieldName) {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "en-IN";
  recognition.start();

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    const number = parseFloat(transcript);
    const inputField = document.querySelector(`input[name=${fieldName}]`);
    if (inputField) {
      if (!isNaN(number)) {
        inputField.value = number;
      } else {
        alert("🎤 Couldn't recognize a number. Try again.");
      }
    }
  };

  recognition.onerror = function (err) {
    alert("🎤 Voice input error: " + err.error);
  };
}

// Logout function
async function logout() {
  try {
    await fetch("http://127.0.0.1:8000/auth/logout", {
      method: "POST",
      credentials: "include"
    });
  } catch (error) {
    console.error("Logout error:", error);
  }
  // Clear dark mode preference and redirect
  localStorage.removeItem("darkMode");
  window.location.href = "login.html";
}

// 📩 Contact Form (agar hai page par)
const contactForm = document.getElementById("contactForm");
if (contactForm) {
  contactForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();

    fetch("http://127.0.0.1:8000/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name, email, message })
    })
      .then(res => res.json())
      .then(data => {
        document.getElementById("contactStatus").textContent = data.message;
      })
      .catch(() => {
        document.getElementById("contactStatus").textContent = "❌ Failed to send.";
      });
  });
}