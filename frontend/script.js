// =============================
// GLOBAL ELEMENTS
// =============================
const modal = document.getElementById("reminderModal");
const taskContainer = document.getElementById("taskContainer");
const emptyState = document.getElementById("emptyState");
const deadlineText = document.getElementById("deadlineText");

let reminders = JSON.parse(localStorage.getItem("studentBuddyReminders")) || [];

// =============================
// INITIAL LOAD
// =============================
document.addEventListener("DOMContentLoaded", () => {
  loadDarkMode();
  renderTasks();
  updateUpcomingDeadline();

  const aiInput = document.getElementById("aiInput");
  if (aiInput) {
    aiInput.addEventListener("keydown", function(event){
      if(event.key === "Enter" && !event.shiftKey){
        event.preventDefault();
        sendAIMessage();
      }
    });
  }
});

// =============================
// AI CHAT
// Tries backend first, then uses frontend fallback
// =============================
async function sendAIMessage(){
  const aiInput = document.getElementById("aiInput");
  const aiResponse = document.getElementById("aiResponse");

  const question = aiInput.value.trim();

  if(question === ""){
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

    if(!res.ok){
      throw new Error("Backend not available");
    }

    const data = await res.json();
    loadingMessage.textContent = data.reply || getDemoAIResponse(question);

  } catch (error) {
    loadingMessage.textContent = getDemoAIResponse(question);
  }
}

function addChatMessage(text, className){
  const aiResponse = document.getElementById("aiResponse");

  const message = document.createElement("div");
  message.className = className;
  message.textContent = text;

  aiResponse.appendChild(message);
  message.scrollIntoView({ behavior: "smooth", block: "nearest" });

  return message;
}

function getDemoAIResponse(question){
  const q = question.toLowerCase();

  if(q.includes("exam") || q.includes("test") || q.includes("quiz")){
    return "Suggested study plan: review key topics first, practise past questions, take short breaks, and add your exam time as a reminder.";
  }

  if(q.includes("assignment") || q.includes("project")){
    return "Break your work into smaller milestones: research, draft, edit, final check, and submission. Add each milestone as a task reminder.";
  }

  if(q.includes("study plan") || q.includes("schedule")){
    return "Try this plan: 25 minutes study, 5 minutes break, then repeat 4 times. Prioritize the subject with the closest deadline.";
  }

  if(q.includes("stress") || q.includes("tired")){
    return "Take a short break, drink water, and list only the top 3 tasks you must finish today. Start with the easiest one to build momentum.";
  }

  if(q.includes("weather")){
    return "I focus on academic productivity. Live weather needs a weather API, but I can help you plan study tasks and reminders.";
  }

  return "I can help with study planning, assignment breakdowns, productivity tips, student FAQs, and reminders. For the strongest demo, connect me to your backend AI API.";
}

function fillPrompt(text){
  const aiInput = document.getElementById("aiInput");
  aiInput.value = text;
  aiInput.focus();
}

// =============================
// MODAL FUNCTIONS
// =============================
function openReminderModal(){
  modal.style.display = "flex";
}

function closeReminderModal(){
  modal.style.display = "none";
}

// =============================
// SAVE REMINDER + LOCAL STORAGE
// =============================
function saveReminder(){
  const title = document.getElementById("taskTitle").value.trim();
  const date = document.getElementById("taskDate").value;
  const time = document.getElementById("taskTime").value;
  const priority = document.getElementById("taskPriority").value;
  const notes = document.getElementById("taskNotes").value.trim();

  if(title === ""){
    alert("Please enter task title");
    return;
  }

  const reminder = {
    id: Date.now(),
    title,
    date,
    time,
    priority,
    notes,
    completed: false
  };

  fetch("http://127.0.0.1:5000/add-reminder", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      task: title,
      date: date,
      time: time
    })
    }
  )
  .then(res => res.json())
  .then(data => console.log("Saved to backend:", data))
  .catch(err => console.log("Backend error:", err));

  reminders.push(reminder);
  saveToLocalStorage();
  renderTasks();
  updateUpcomingDeadline();

  closeReminderModal();
  clearReminderForm();
  showTaskList();
}

function saveToLocalStorage(){
  localStorage.setItem("studentBuddyReminders", JSON.stringify(reminders));
}

function clearReminderForm(){
  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDate").value = "";
  document.getElementById("taskTime").value = "";
  document.getElementById("taskPriority").value = "Medium";
  document.getElementById("taskNotes").value = "";
}

// =============================
// RENDER TASKS
// =============================
function renderTasks(){
  if(!taskContainer) return;

  taskContainer.innerHTML = "";

  if(reminders.length === 0){
    if(emptyState) emptyState.style.display = "block";
    return;
  }

  if(emptyState) emptyState.style.display = "none";

  const sortedReminders = [...reminders].sort((a, b) => {
    const dateA = new Date(`${a.date || "9999-12-31"}T${a.time || "23:59"}`);
    const dateB = new Date(`${b.date || "9999-12-31"}T${b.time || "23:59"}`);
    return dateA - dateB;
  });

  sortedReminders.forEach(reminder => {
    const taskCard = document.createElement("div");
    taskCard.className = `task-card ${reminder.completed ? "completed" : ""}`;

    taskCard.innerHTML = `
      <div class="task-top">
        <h3>${escapeHTML(reminder.title)}</h3>
        <span class="priority ${reminder.priority.toLowerCase()}">${reminder.priority}</span>
      </div>

      <p><strong>Date:</strong> ${reminder.date || "Not set"}</p>
      <p><strong>Time:</strong> ${reminder.time || "Not set"}</p>
      <p><strong>Notes:</strong> ${escapeHTML(reminder.notes) || "No notes"}</p>

      <div class="task-buttons">
        <button class="done-btn" onclick="toggleDone(${reminder.id})">
          ${reminder.completed ? "Undo" : "Done"}
        </button>
        <button class="delete-btn" onclick="deleteTask(${reminder.id})">Delete</button>
      </div>
    `;

    taskContainer.appendChild(taskCard);
  });
}

function toggleDone(id){
  reminders = reminders.map(reminder => {
    if(reminder.id === id){
      return { ...reminder, completed: !reminder.completed };
    }
    return reminder;
  });

  saveToLocalStorage();
  renderTasks();
  updateUpcomingDeadline();
}

function deleteTask(id){
  reminders = reminders.filter(reminder => reminder.id !== id);
  saveToLocalStorage();
  renderTasks();
  updateUpcomingDeadline();
}

function clearCompleted(){
  reminders = reminders.filter(reminder => !reminder.completed);
  saveToLocalStorage();
  renderTasks();
  updateUpcomingDeadline();
}

// =============================
// UPCOMING DEADLINE
// =============================
function updateUpcomingDeadline(){
  if(!deadlineText) return;

  const upcoming = reminders
    .filter(reminder => !reminder.completed && reminder.date)
    .sort((a, b) => {
      const dateA = new Date(`${a.date}T${a.time || "23:59"}`);
      const dateB = new Date(`${b.date}T${b.time || "23:59"}`);
      return dateA - dateB;
    })[0];

  if(!upcoming){
    deadlineText.textContent = "No reminders yet. Add your first task.";
    return;
  }

  deadlineText.textContent = `${upcoming.title} — ${formatDate(upcoming.date)} ${upcoming.time ? "at " + upcoming.time : ""}`;
}

function formatDate(dateString){
  const date = new Date(dateString);
  return date.toLocaleDateString("en-MY", {
    weekday: "short",
    day: "numeric",
    month: "short"
  });
}

// =============================
// FAQ ACCORDION
// =============================
function toggleFAQ(card){
  card.classList.toggle("open");
}

// =============================
// SCROLL FUNCTIONS
// =============================
function showTaskList(){
  document.getElementById("taskSection").scrollIntoView({
    behavior: "smooth"
  });
}

function showFAQ(){
  document.getElementById("faqSection").scrollIntoView({
    behavior: "smooth"
  });
}

// =============================
// DARK MODE
// =============================
function toggleDarkMode(){
  document.body.classList.toggle("dark-mode");
  localStorage.setItem("studentBuddyDarkMode", document.body.classList.contains("dark-mode"));
}

function loadDarkMode(){
  const isDark = localStorage.getItem("studentBuddyDarkMode") === "true";
  if(isDark){
    document.body.classList.add("dark-mode");
  }
}

// =============================
// SMALL SECURITY HELPER
// =============================
function escapeHTML(text){
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
