/* ─── State ──────────────────────────────────────────────────────── */
let completedCourses = [];
let chatHistory = [];
let catalogData = [];
let activeCategory = "All";
let selectedRating = 0;

/* ─── Tab Navigation ─────────────────────────────────────────────── */
document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(s => s.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");

        if (tab.dataset.tab === "catalog" && catalogData.length === 0) loadCatalog();
        if (tab.dataset.tab === "reviews") loadReviewDropdowns();
    });
});

/* ─── Drag & Drop Upload ──────────────────────────────────────────── */
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");

dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") processFile(file);
    else showStatus("uploadStatus", "Please upload a PDF file.", "error");
});
dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) processFile(fileInput.files[0]);
});

async function processFile(file) {
    showStatus("uploadStatus", "⏳ Parsing transcript...", "loading");
    document.getElementById("uploadResults").classList.add("hidden");
    document.getElementById("schedulePreview").classList.add("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/upload", { method: "POST", body: formData });
        const data = await res.json();
        if (data.error) { showStatus("uploadStatus", data.error, "error"); return; }

        completedCourses = data.courses;
        showStatus("uploadStatus", `✓ Found ${data.courses.length} completed courses.`, "success");

        renderCompletedCourses(data.courses);
        renderEligible(data.eligible_now);
        document.getElementById("uploadResults").classList.remove("hidden");

        renderSchedule(data.schedule, "previewSemesters", true);
        document.getElementById("schedulePreview").classList.remove("hidden");

        // Pre-fill schedule tab
        document.getElementById("manualCourses").value = data.courses.join(", ");
    } catch (err) {
        showStatus("uploadStatus", "Failed to process file. Is it a valid PDF transcript?", "error");
    }
}

function renderCompletedCourses(courses) {
    const el = document.getElementById("completedList");
    el.innerHTML = courses.map(c =>
        `<span class="course-tag" onclick="openCourseModal('${c}')">${c}</span>`
    ).join("");
}

function renderEligible(courses) {
    const el = document.getElementById("eligibleList");
    if (!courses || courses.length === 0) {
        el.innerHTML = `<p style="color:var(--muted);font-size:13px">No suggestions — all prerequisites may already be met.</p>`;
        return;
    }
    el.innerHTML = courses.map(c => `
        <div class="eligible-item" onclick="openCourseModal('${c.id}')">
            <div class="eligible-id">${c.id}</div>
            <div class="eligible-name">${c.name}</div>
        </div>
    `).join("");
}

/* ─── Schedule Generator ──────────────────────────────────────────── */
document.getElementById("generateBtn").addEventListener("click", async () => {
    const raw = document.getElementById("manualCourses").value;
    const completed = raw.split(",").map(s => s.trim()).filter(Boolean);
    const sems = parseInt(document.getElementById("semCount").value);
    const perSem = parseInt(document.getElementById("perSem").value);

    const btn = document.getElementById("generateBtn");
    btn.textContent = "Generating...";
    btn.disabled = true;

    try {
        const res = await fetch("/schedule", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ completed, semesters: sems, per_semester: perSem })
        });
        const data = await res.json();
        completedCourses = completed;
        renderSchedule(data.schedule, "scheduleOutput", false);
    } catch (err) {
        console.error(err);
    } finally {
        btn.textContent = "Generate Schedule";
        btn.disabled = false;
    }
});

function renderSchedule(schedule, containerId, compact) {
    const container = document.getElementById(containerId);
    if (!schedule || schedule.length === 0) {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">🎓</div><p>No remaining courses found! You may be done.</p></div>`;
        return;
    }
    container.innerHTML = schedule.map(sem => `
        <div class="semester-card">
            <div class="semester-label">${sem.label}</div>
            ${sem.courses.length === 0
                ? `<p style="color:var(--muted);font-size:13px">No courses scheduled.</p>`
                : sem.courses.map(c => `
                    <div class="sem-course" onclick="openCourseModal('${c.id}')">
                        <div class="sem-course-id">${c.id}</div>
                        <div class="sem-course-info">
                            <div class="sem-course-name">${c.name}</div>
                            <div class="sem-course-cat">${c.category}</div>
                        </div>
                        <div class="units-badge">${c.units}u</div>
                    </div>
                `).join("")
            }
        </div>
    `).join("");
}

/* ─── Course Catalog ──────────────────────────────────────────────── */
async function loadCatalog() {
    try {
        const res = await fetch("/catalog");
        const data = await res.json();
        catalogData = data.catalog;
        buildCategoryFilters();
        renderCatalog(catalogData);
    } catch (err) {
        console.error("Failed to load catalog", err);
    }
}

function buildCategoryFilters() {
    const categories = ["All", ...new Set(catalogData.map(c => c.category))];
    const el = document.getElementById("categoryFilters");
    el.innerHTML = categories.map(cat => `
        <span class="chip ${cat === "All" ? "active" : ""}" onclick="filterCatalog('${cat}', this)">${cat}</span>
    `).join("");
}

function filterCatalog(category, chipEl) {
    activeCategory = category;
    document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
    chipEl.classList.add("active");
    applyFilters();
}

document.getElementById("catalogSearch").addEventListener("input", applyFilters);

function applyFilters() {
    const query = document.getElementById("catalogSearch").value.toLowerCase();
    const filtered = catalogData.filter(c => {
        const matchCat = activeCategory === "All" || c.category === activeCategory;
        const matchSearch = !query ||
            c.id.toLowerCase().includes(query) ||
            c.name.toLowerCase().includes(query) ||
            c.description.toLowerCase().includes(query);
        return matchCat && matchSearch;
    });
    renderCatalog(filtered);
}

function getCatClass(category) {
    const map = {
        "Lower Division Core": "cat-lower",
        "Upper Division Core": "cat-upper",
        "Math": "cat-math",
        "Elective": "cat-elec",
        "Senior Project": "cat-senior"
    };
    return map[category] || "cat-elec";
}

function renderCatalog(courses) {
    const grid = document.getElementById("catalogGrid");
    if (courses.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🔍</div><p>No courses match your search.</p></div>`;
        return;
    }
    grid.innerHTML = courses.map(c => {
        const stars = renderStars(c.avg_rating);
        const prereqs = c.prerequisites.length > 0
            ? c.prerequisites.join(", ")
            : "None";
        return `
            <div class="catalog-card" onclick="openCourseModal('${c.id}')">
                <div class="catalog-card-header">
                    <span class="catalog-id">${c.id}</span>
                    <span class="catalog-cat-badge ${getCatClass(c.category)}">${c.category}</span>
                </div>
                <div class="catalog-name">${c.name}</div>
                <div class="catalog-desc">${c.description}</div>
                <div class="catalog-meta">
                    <div class="prereq-list">Pre: ${prereqs}</div>
                    <div class="rating-display">
                        ${stars}
                        ${c.review_count > 0 ? `<span style="color:var(--muted);font-size:12px">(${c.review_count})</span>` : ""}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

function renderStars(avg) {
    if (!avg) return `<span style="color:var(--muted);font-size:12px">No ratings</span>`;
    return Array.from({length: 5}, (_, i) =>
        `<span class="${i < Math.round(avg) ? 'star-filled' : 'star-empty'}">★</span>`
    ).join("");
}

/* ─── Course Modal ────────────────────────────────────────────────── */
async function openCourseModal(courseId) {
    if (catalogData.length === 0) {
        const res = await fetch("/catalog");
        const data = await res.json();
        catalogData = data.catalog;
    }

    const course = catalogData.find(c => c.id === courseId);
    if (!course) return;

    const reviews = await fetch(`/reviews/${encodeURIComponent(courseId)}`).then(r => r.json());
    const prereqsHtml = course.prerequisites.length
        ? course.prerequisites.map(p => `<span class="modal-prereq-tag">${p}</span>`).join("")
        : `<span style="color:var(--muted)">None</span>`;

    const reviewsHtml = reviews.reviews.length > 0
        ? reviews.reviews.map(r => `
            <div class="review-item">
                <div class="review-header">
                    <div class="review-prof">${r.professor}</div>
                    <div class="review-stars">${"★".repeat(r.rating)}${"☆".repeat(5 - r.rating)}</div>
                </div>
                <div class="review-meta">${r.author} · ${r.date}</div>
                <div class="review-comment">${r.comment}</div>
            </div>
        `).join("")
        : `<p class="no-reviews">No reviews yet. Be the first!</p>`;

    document.getElementById("modalContent").innerHTML = `
        <div class="modal-course-id">${course.id} · ${course.units} units</div>
        <div class="modal-course-name">${course.name}</div>
        <div class="modal-section">
            <div class="modal-section-label">Description</div>
            <p style="color:var(--muted);font-size:14px;line-height:1.6">${course.description}</p>
        </div>
        <div class="modal-section">
            <div class="modal-section-label">Prerequisites</div>
            <div class="modal-prereqs">${prereqsHtml}</div>
        </div>
        <div class="modal-section">
            <div class="modal-section-label">Category</div>
            <span class="catalog-cat-badge ${getCatClass(course.category)}">${course.category}</span>
        </div>
        ${reviews.average ? `
        <div class="modal-section">
            <div class="modal-section-label">Average Rating</div>
            <div class="rating-display">${renderStars(reviews.average)} <span style="color:var(--muted);font-size:13px">${reviews.average}/5</span></div>
        </div>` : ""}
        <div class="modal-section">
            <div class="modal-section-label">Student Reviews</div>
            ${reviewsHtml}
        </div>
    `;

    document.getElementById("courseModal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("courseModal").classList.add("hidden");
}

/* ─── Reviews ────────────────────────────────────────────────────── */
async function loadReviewDropdowns() {
    if (catalogData.length === 0) {
        const res = await fetch("/catalog");
        const data = await res.json();
        catalogData = data.catalog;
    }
    const options = catalogData.map(c => `<option value="${c.id}">${c.id} – ${c.name}</option>`).join("");
    document.getElementById("reviewCourse").innerHTML = options;
    document.getElementById("viewCourse").innerHTML = options;
    loadReviews(catalogData[0]?.id);
}

// Star picker
document.getElementById("starPicker").querySelectorAll(".star").forEach(star => {
    star.addEventListener("click", () => {
        selectedRating = parseInt(star.dataset.val);
        document.getElementById("reviewRating").value = selectedRating;
        document.querySelectorAll(".star").forEach((s, i) => {
            s.classList.toggle("lit", i < selectedRating);
        });
    });
    star.addEventListener("mouseover", () => {
        const val = parseInt(star.dataset.val);
        document.querySelectorAll(".star").forEach((s, i) => s.classList.toggle("lit", i < val));
    });
    star.addEventListener("mouseout", () => {
        document.querySelectorAll(".star").forEach((s, i) => s.classList.toggle("lit", i < selectedRating));
    });
});

document.getElementById("submitReview").addEventListener("click", async () => {
    const courseId = document.getElementById("reviewCourse").value;
    const professor = document.getElementById("reviewProf").value.trim();
    const rating = parseInt(document.getElementById("reviewRating").value);
    const comment = document.getElementById("reviewComment").value.trim();
    const author = document.getElementById("reviewAuthor").value.trim() || "Anonymous";

    if (!professor) { showStatus("reviewStatus", "Please enter a professor name.", "error"); return; }
    if (!rating) { showStatus("reviewStatus", "Please select a rating.", "error"); return; }
    if (!comment) { showStatus("reviewStatus", "Please write a comment.", "error"); return; }

    const btn = document.getElementById("submitReview");
    btn.textContent = "Submitting...";
    btn.disabled = true;

    try {
        const res = await fetch("/reviews", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ course_id: courseId, professor, rating, comment, author })
        });
        const data = await res.json();
        if (data.success) {
            showStatus("reviewStatus", "✓ Review submitted! Thank you.", "success");
            document.getElementById("reviewProf").value = "";
            document.getElementById("reviewComment").value = "";
            selectedRating = 0;
            document.getElementById("reviewRating").value = 0;
            document.querySelectorAll(".star").forEach(s => s.classList.remove("lit"));
            loadReviews(courseId);
        }
    } catch (err) {
        showStatus("reviewStatus", "Failed to submit review.", "error");
    } finally {
        btn.textContent = "Submit Review";
        btn.disabled = false;
    }
});

async function loadReviews(courseId) {
    if (!courseId) return;
    try {
        const res = await fetch(`/reviews/${encodeURIComponent(courseId)}`);
        const data = await res.json();
        const el = document.getElementById("reviewsList");
        if (data.reviews.length === 0) {
            el.innerHTML = `<p class="no-reviews">No reviews yet for this course.</p>`;
        } else {
            el.innerHTML = data.reviews.map(r => `
                <div class="review-item">
                    <div class="review-header">
                        <div class="review-prof">${r.professor}</div>
                        <div class="review-stars">${"★".repeat(r.rating)}${"☆".repeat(5 - r.rating)}</div>
                    </div>
                    <div class="review-meta">${r.author} · ${r.date}</div>
                    <div class="review-comment">${r.comment}</div>
                </div>
            `).join("");
        }
    } catch (err) {
        console.error(err);
    }
}

/* ─── AI Chat ─────────────────────────────────────────────────────── */
async function sendChat() {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();
    if (!msg) return;

    input.value = "";
    addChatMsg("user", msg);
    chatHistory.push({ role: "user", content: msg });

    const typingId = addChatMsg("assistant", "Thinking...", true);

    try {
        // Get system prompt with course context from our server
        const sysRes = await fetch("/chat/system-prompt", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ completed_courses: completedCourses })
        });
        const { system_prompt } = await sysRes.json();

        // Call Anthropic API directly from frontend
        const response = await fetch("https://api.anthropic.com/v1/messages", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: "claude-sonnet-4-20250514",
                max_tokens: 1000,
                system: system_prompt,
                messages: chatHistory
            })
        });

        const data = await response.json();
        const reply = data.content?.find(b => b.type === "text")?.text || "Sorry, I couldn't generate a response.";

        chatHistory.push({ role: "assistant", content: reply });
        updateChatMsg(typingId, reply);
    } catch (err) {
        updateChatMsg(typingId, "Sorry, I'm having trouble connecting right now. Please try again.");
    }
}

let msgCounter = 0;
function addChatMsg(role, text, isTyping = false) {
    const id = `msg-${++msgCounter}`;
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    div.id = id;
    div.innerHTML = `<div class="msg-bubble ${isTyping ? "typing" : ""}">${escapeHtml(text)}</div>`;
    document.getElementById("chatMessages").appendChild(div);
    document.getElementById("chatMessages").scrollTop = 9999;
    return id;
}

function updateChatMsg(id, text) {
    const el = document.getElementById(id);
    if (el) {
        el.querySelector(".msg-bubble").className = "msg-bubble";
        el.querySelector(".msg-bubble").innerHTML = formatChatText(text);
        document.getElementById("chatMessages").scrollTop = 9999;
    }
}

function formatChatText(text) {
    // Simple markdown-ish formatting
    return escapeHtml(text)
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.*?)`/g, `<code style="background:var(--surface2);padding:1px 5px;border-radius:4px;font-family:var(--font-mono);font-size:12px">$1</code>`)
        .replace(/\n/g, "<br>");
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ─── Helpers ─────────────────────────────────────────────────────── */
function showStatus(id, msg, type) {
    const el = document.getElementById(id);
    el.textContent = msg;
    el.className = `status-msg ${type}`;
    el.classList.remove("hidden");
}

// Keyboard shortcut for chat
document.getElementById("chatInput").addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChat(); }
});