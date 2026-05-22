// =============================
// GLOBAL ELEMENTS
// =============================
const modal = document.getElementById("reminderModal");
const taskContainer = document.getElementById("taskContainer");


// =============================
// ✅ AI CHAT (CONNECTED TO BACKEND)
// =============================
async function sendAIMessage(){

    const aiInput = document.getElementById("aiInput");
    const aiResponse = document.getElementById("aiResponse");

    const question = aiInput.value.trim();

    if(question === ""){
        alert("Please type something first");
        return;
    }

    try {
        // ✅ SEND MESSAGE TO BACKEND
        const res = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: question })
        });

        const data = await res.json();

        // ✅ DISPLAY CHAT (KEEP YOUR STYLE)
        aiResponse.innerHTML += `
            <div class="ai-user-message">
                ${question}
            </div>

            <div class="ai-bot-message">
                ${data.response}
            </div>
        `;

    } catch (error) {
        aiResponse.innerHTML += `
            <div style="color:red;">Error connecting to backend</div>
        `;
        console.error(error);
    }

    aiInput.value = "";
}



// =============================
// ✅ MODAL FUNCTIONS
// =============================
function openReminderModal(){
    modal.style.display = "flex";
}

function closeReminderModal(){
    modal.style.display = "none";
}



// =============================
// ✅ SAVE REMINDER
// =============================
function saveReminder(){

    const title = document.getElementById("taskTitle").value;
    const date = document.getElementById("taskDate").value;
    const time = document.getElementById("taskTime").value;
    const notes = document.getElementById("taskNotes").value;

    if(title === ""){
        alert("Please enter task title");
        return;
    }

    const taskCard = document.createElement("div");
    taskCard.classList.add("task-card");

    taskCard.innerHTML = `
        <h3>${title}</h3>
        <p><strong>Date:</strong> ${date}</p>
        <p><strong>Time:</strong> ${time}</p>
        <p><strong>Notes:</strong> ${notes}</p>
        <button onclick="deleteTask(this)">Delete</button>
    `;

    taskContainer.prepend(taskCard);

    closeReminderModal();

    // Clear inputs
    document.getElementById("taskTitle").value = "";
    document.getElementById("taskDate").value = "";
    document.getElementById("taskTime").value = "";
    document.getElementById("taskNotes").value = "";
}



// =============================
// ✅ DELETE TASK
// =============================
function deleteTask(button){
    button.parentElement.remove();
}



// =============================
// ✅ SCROLL FUNCTIONS
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

function showUpcoming(){
    document.getElementById("taskSection").scrollIntoView({
        behavior: "smooth"
    });
}