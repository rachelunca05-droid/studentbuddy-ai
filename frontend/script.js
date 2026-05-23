// ==========================================
// GLOBAL INITIALIZATION CONSTANTS
// ==========================================
const modal = document.getElementById("reminderModal");
const deadlineText = document.getElementById("deadlineText");

// ==========================================
// APPS SYSTEM LIFE CYCLE BOOTSTRAP
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  loadDarkMode();

  const aiInput = document.getElementById("aiInput");
  if (aiInput) {
    aiInput.addEventListener("keydown", function(event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendAIMessage();
      }
    });
  }
});

// ==========================================
// TRANSACTIONAL LIVE INTERACTIVE CHAT PIPELINE
// ==========================================
async function sendAIMessage() {
  const aiInput = document.getElementById("aiInput");
  const question = aiInput.value.trim();

  if (question === "") {
    alert("Please type something first");
    return;
  }

  addChatMessage(question, "ai-user-message");
  aiInput.value = "";

  const loadingMessage = addChatMessage("StudentBuddy is thinking...", "ai-bot-message");

  try {
    const res = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: question })
    });

    if (!res.ok) {
      throw new Error("Backend connection disrupted");
    }

    const data = await res.json();
    loadingMessage.textContent = data.reply || getDemoAIResponse(question);

  } catch (error) {
    loadingMessage.textContent = getDemoAIResponse(question);
  }
}

function addChatMessage(text, className) {
  const aiResponse = document.getElementById("aiResponse");

  const message = document.createElement("div");
  message.className = className;
  message.textContent = text;

  aiResponse.appendChild(message);
  
  // Smoothly pushes up older logs away from input area during active generation
  aiResponse.scrollTop = aiResponse.scrollHeight;

  return message;
}

function getDemoAIResponse(question) {
  const q = question.toLowerCase();
  if (q.includes("exam") || q.includes("test")) return "Review core normalization topics, SQL scripts, and run verification loops.";
  if (q.includes("stress") || q.includes("tired")) return "Pause for a moment, take a deep breath, and split your current goal down into one small step.";
  return "I am connected to your live intelligence tracking system. Ask me anything about university life!";
}

function fillPrompt(text) {
  const aiInput = document.getElementById("aiInput");
  aiInput.value = text;
  aiInput.focus();
}

// ==========================================
// SYSTEM MODAL & ACCESSORIES CONFIGS
// ==========================================
function openReminderModal() { if (modal) modal.style.display = "flex"; }
function closeReminderModal() { if (modal) modal.style.display = "none"; }
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem("studentBuddyDarkMode", document.body.classList.contains("dark-mode"));
}
function loadDarkMode() {
  if (localStorage.getItem("studentBuddyDarkMode") === "true") {
    document.body.classList.add("dark-mode");
  }
}