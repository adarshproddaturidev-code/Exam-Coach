/* ─── app.js ─── Personalized Entrance Exam Coach ─── */
"use strict";

const API = "http://localhost:8000";
let studentId = () => parseInt(document.getElementById("student-id-input").value) || 1;

// Chart instances — kept so we can destroy before re-rendering
let charts = {};

/* ══════════════ UTILS ══════════════════════════════════════════════════════ */
function showToast(msg, type = "success") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = `toast ${type}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.className = "toast hidden"; }, 4000);
}

function showLoader(msg = "Processing…") {
  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("loader-msg").textContent = msg;
}
function hideLoader() {
  document.getElementById("loader").classList.add("hidden");
}

async function apiCall(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

function destroyChart(key) {
  if (charts[key]) { charts[key].destroy(); delete charts[key]; }
}

/* ══════════════ TABS ════════════════════════════════════════════════════════ */
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`panel-${btn.dataset.tab}`).classList.add("active");
    // Auto-refresh dashboard when navigating to it
    if (btn.dataset.tab === "dashboard") loadDashboard();
  });
});

/* ══════════════ TAB 1: SUBMIT TEST ════════════════════════════════════════ */
document.getElementById("load-sample-btn").addEventListener("click", async () => {
  try {
    const resp = await fetch("../sample_data/mock_test_sample.json");
    const text = await resp.text();
    document.getElementById("json-input").value = text;
    showToast("Sample data loaded!", "success");
  } catch {
    // Fallback: fetch from backend-served root, or hardcode tiny sample
    const mini = {
      "student_id": 1,
      "questions": [
        {"subject":"Physics","topic":"Laws of Motion","question_id":"Q1","student_answer":"B","correct_answer":"A","time_taken":95},
        {"subject":"Chemistry","topic":"Organic Chemistry","question_id":"Q2","student_answer":"C","correct_answer":"C","time_taken":60},
        {"subject":"Mathematics","topic":"Calculus","question_id":"Q3","student_answer":"A","correct_answer":"D","time_taken":180}
      ]
    };
    document.getElementById("json-input").value = JSON.stringify(mini, null, 2);
    showToast("Loaded mini sample (full file not found via file:// — run via server).", "success");
  }
});

document.getElementById("submit-btn").addEventListener("click", async () => {
  const raw = document.getElementById("json-input").value.trim();
  if (!raw) { showToast("Please paste or load JSON first.", "error"); return; }

  let payload;
  try {
    payload = JSON.parse(raw);
    payload.student_id = studentId();
  } catch {
    showToast("Invalid JSON — please check the format.", "error");
    return;
  }

  showLoader("Analysing your test…");
  try {
    const res = await apiCall("/api/tests/submit", "POST", payload);
    const box = document.getElementById("submit-result");
    box.classList.remove("hidden", "error");
    box.innerHTML = `
      <strong>✅ Test submitted successfully!</strong><br>
      Total Questions: <strong>${res.total_questions}</strong> &nbsp;|&nbsp;
      Correct: <strong>${res.correct}</strong> &nbsp;|&nbsp;
      Accuracy: <strong>${res.accuracy}%</strong><br>
      Mock Test ID: <code>${res.mock_test_id}</code> — 
      Weakness scores updated automatically.`;
    showToast("Test analysed! Navigate to 'Weak Topics' tab.", "success");
  } catch (e) {
    const box = document.getElementById("submit-result");
    box.classList.remove("hidden");
    box.classList.add("error");
    box.textContent = "Error: " + e.message;
    showToast(e.message, "error");
  } finally {
    hideLoader();
  }
});

/* ══════════════ TAB 2: ANALYSIS ═══════════════════════════════════════════ */
function subjectTagClass(subject) {
  const s = (subject || "").toLowerCase();
  if (s.includes("physics")) return "tag-physics";
  if (s.includes("chem"))    return "tag-chemistry";
  if (s.includes("math"))    return "tag-mathematics";
  return "tag-default";
}

function weaknessColor(score) {
  if (score >= 0.65) return "#f87171";
  if (score >= 0.4)  return "#fb923c";
  return "#22d3a6";
}

function renderTopicCard(t) {
  const isWeak = t.rank <= Math.ceil(t.rank); // all ranked
  const isWeakCategory = t.weakness_score >= 0.4;
  const col = weaknessColor(t.weakness_score);
  return `
  <div class="topic-card ${isWeakCategory ? 'weak' : 'strong'}">
    <div class="topic-rank">Rank #${t.rank}</div>
    <div class="topic-title">${t.topic}</div>
    <span class="topic-subject-tag ${subjectTagClass(t.subject)}">${t.subject}</span>
    <div class="score-row">
      <div class="score-item"><label>Error Rate</label><span style="color:${t.error_rate > 0.5 ? 'var(--red)' : 'var(--green)'}">${(t.error_rate*100).toFixed(0)}%</span></div>
      <div class="score-item"><label>Avg Time</label><span>${t.avg_time.toFixed(1)}s</span></div>
      <div class="score-item"><label>Mistakes</label><span>${t.mistake_freq}</span></div>
    </div>
    <div class="ws-bar-wrap">
      <div class="ws-bar-track">
        <div class="ws-bar-fill" style="width:${Math.min(t.weakness_score*100, 100).toFixed(1)}%; background:${col};"></div>
      </div>
      <div class="ws-label"><span>Weakness Score</span><span style="color:${col};font-weight:700">${t.weakness_score.toFixed(3)}</span></div>
    </div>
  </div>`;
}

async function loadAnalysis() {
  showLoader("Loading analysis…");
  try {
    const data = await apiCall(`/api/analysis/${studentId()}`);
    document.getElementById("stat-total").textContent    = data.total_questions;
    document.getElementById("stat-correct").textContent  = data.total_correct;
    document.getElementById("stat-accuracy").textContent = data.accuracy + "%";
    document.getElementById("stat-weak-count").textContent = data.weak_topics.length;

    const grid = document.getElementById("topics-grid");
    const allTopics = [...data.weak_topics, ...data.strong_topics];
    if (allTopics.length === 0) {
      grid.innerHTML = '<div class="placeholder-msg">No topic data yet. Submit a test first.</div>';
    } else {
      grid.innerHTML = allTopics.map(renderTopicCard).join("");
    }
    showToast("Analysis loaded!", "success");
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    hideLoader();
  }
}

document.getElementById("refresh-analysis-btn").addEventListener("click", loadAnalysis);

/* ══════════════ TAB 3: STUDY PLAN ════════════════════════════════════════ */
function renderPlan(plan) {
  const container = document.getElementById("plan-container");
  if (!plan.days || plan.days.length === 0) {
    container.innerHTML = '<div class="placeholder-msg">No plan data returned.</div>';
    return;
  }
  container.innerHTML = plan.days.map(day => `
    <div class="day-card" id="day-${day.day}">
      <div class="day-header" onclick="toggleDay(${day.day})">
        <div>
          <div class="day-num">${day.date_label || `Day ${day.day}`}</div>
          <div class="day-focus">${day.focus}</div>
        </div>
        <div class="day-meta">
          <span>⏱ ${day.duration_hours}h</span>
          <span>📝 ${day.practice_questions} Qs</span>
        </div>
        <span class="day-chevron">▼</span>
      </div>
      <div class="day-body">
        <ul class="blocks-list">
          ${(day.revision_blocks || []).map(b => `<li>${b}</li>`).join("")}
        </ul>
        <div class="day-tip">💡 ${day.tip || "Stay consistent — every hour of focused study counts!"}</div>
      </div>
    </div>
  `).join("");
  // Open first day
  toggleDay(plan.days[0].day);
}

window.toggleDay = function(n) {
  const card = document.getElementById(`day-${n}`);
  if (card) card.classList.toggle("open");
};

document.getElementById("gen-plan-btn").addEventListener("click", async () => {
  showLoader("Generating your 7-day study plan with AI…");
  try {
    const data = await apiCall(`/api/study-plan/${studentId()}`, "POST");
    renderPlan(data.plan);
    showToast("Study plan generated!", "success");
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    hideLoader();
  }
});

document.getElementById("load-plan-btn").addEventListener("click", async () => {
  showLoader("Loading latest plan…");
  try {
    const data = await apiCall(`/api/study-plan/${studentId()}/latest`);
    renderPlan(data.plan);
    showToast("Latest plan loaded!", "success");
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    hideLoader();
  }
});

/* ══════════════ TAB 4: RECOMMENDATIONS ═══════════════════════════════════ */
function renderRecs(data) {
  const container = document.getElementById("recs-container");
  const list = data.recommendations || [];
  if (list.length === 0) {
    container.innerHTML = '<div class="placeholder-msg">No recommendations yet.</div>';
    return;
  }
  container.innerHTML = list.map(r => `
    <div class="rec-card">
      <div class="rec-header">
        <div>
          <div class="rec-title">${r.topic}</div>
          <span class="topic-subject-tag ${subjectTagClass(r.subject)}">${r.subject}</span>
        </div>
      </div>
      <div class="why-box">⚠️ ${r.why_weak}</div>
      <div class="rec-sections">
        <div class="rec-section">
          <h4>📖 Concept Revision</h4>
          <ul>${(r.concept_revision||[]).map(x=>`<li>${x}</li>`).join("")}</ul>
        </div>
        <div class="rec-section">
          <h4>✏️ Practice Exercises</h4>
          <ul>${(r.practice_exercises||[]).map(x=>`<li>${x}</li>`).join("")}</ul>
        </div>
        <div class="rec-section">
          <h4>📄 Mock Tests</h4>
          <ul>${(r.mock_tests||[]).map(x=>`<li>${x}</li>`).join("")}</ul>
        </div>
      </div>
      <div class="resources-row">
        ${(r.resources||[]).map(res=>`
          <a href="${res.url}" target="_blank" rel="noopener" class="resource-chip ${res.type}">
            ${res.type === 'youtube' ? '▶ ' : '🔗 '}${res.title}
          </a>`).join("")}
      </div>
      <div class="rec-tip">🌟 ${r.improvement_tip}</div>
    </div>
  `).join("");
}

document.getElementById("gen-recs-btn").addEventListener("click", async () => {
  showLoader("Generating recommendations with AI…");
  try {
    const data = await apiCall(`/api/recommendations/${studentId()}`, "POST");
    renderRecs(data.recommendations);
    showToast("Recommendations generated!", "success");
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    hideLoader();
  }
});

document.getElementById("load-recs-btn").addEventListener("click", async () => {
  showLoader("Loading latest recommendations…");
  try {
    const data = await apiCall(`/api/recommendations/${studentId()}/latest`);
    renderRecs(data.recommendations);
    showToast("Recommendations loaded!", "success");
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    hideLoader();
  }
});

/* ══════════════ TAB 5: DASHBOARD ══════════════════════════════════════════ */
const CHART_DEFAULTS = {
  color: "#94a3b8",
  borderColor: "#1e293b",
  plugins: {
    legend: { labels: { color: "#94a3b8", font: { family: "Inter", size: 11 } } },
    tooltip: { backgroundColor: "#1e293b", titleColor: "#f1f5f9", bodyColor: "#94a3b8" },
  },
  scales: {
    x: { ticks: { color: "#64748b" }, grid: { color: "rgba(255,255,255,0.05)" } },
    y: { ticks: { color: "#64748b" }, grid: { color: "rgba(255,255,255,0.05)" } },
  },
};

async function loadDashboard() {
  showLoader("Loading dashboard…");
  try {
    const data = await apiCall(`/api/progress/${studentId()}`);
    renderDashboard(data);
    showToast("Dashboard refreshed!", "success");
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    hideLoader();
  }
}

function renderDashboard(data) {
  const history = data.history || [];
  const topics  = data.topic_scores || [];

  // ── Accuracy Over Time ──
  destroyChart("accuracy");
  const accCtx = document.getElementById("accuracyChart").getContext("2d");
  charts.accuracy = new Chart(accCtx, {
    type: "line",
    data: {
      labels: history.map(h => `Test ${h.test_number}`),
      datasets: [{
        label: "Accuracy (%)",
        data: history.map(h => h.accuracy),
        borderColor: "#6C63FF", backgroundColor: "rgba(108,99,255,0.12)",
        tension: 0.4, fill: true, pointBackgroundColor: "#6C63FF", pointRadius: 5,
      }],
    },
    options: { ...CHART_DEFAULTS, responsive: true, maintainAspectRatio: false,
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, min: 0, max: 100 } } },
  });

  // ── Weak vs Strong ──
  destroyChart("topicPie");
  const pieCtx = document.getElementById("topicChart").getContext("2d");
  const weakCount   = topics.filter(t => t.weakness_score >= 0.4).length;
  const strongCount = topics.length - weakCount;
  charts.topicPie = new Chart(pieCtx, {
    type: "doughnut",
    data: {
      labels: ["Weak Topics", "Strong Topics"],
      datasets: [{ data: [weakCount, strongCount],
        backgroundColor: ["rgba(248,113,113,0.8)", "rgba(34,211,166,0.8)"],
        borderColor: "rgba(255,255,255,0.1)", borderWidth: 2,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: CHART_DEFAULTS.plugins.legend,
        tooltip: CHART_DEFAULTS.plugins.tooltip,
      },
    },
  });

  // ── Weakness Score Bar ──
  destroyChart("weakness");
  const wkCtx = document.getElementById("weaknessChart").getContext("2d");
  const top8 = topics.slice(0, 8);
  charts.weakness = new Chart(wkCtx, {
    type: "bar",
    data: {
      labels: top8.map(t => t.topic.length > 15 ? t.topic.slice(0,14)+"…" : t.topic),
      datasets: [{
        label: "Weakness Score",
        data: top8.map(t => t.weakness_score),
        backgroundColor: top8.map(t => t.weakness_score >= 0.65
          ? "rgba(248,113,113,0.8)" : t.weakness_score >= 0.4
          ? "rgba(251,146,60,0.8)" : "rgba(34,211,166,0.8)"),
        borderRadius: 6,
      }],
    },
    options: {
      ...CHART_DEFAULTS, responsive: true, maintainAspectRatio: false,
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, min: 0, max: 1 } },
    },
  });

  // ── Avg Time per Test ──
  destroyChart("time");
  const tmCtx = document.getElementById("timeChart").getContext("2d");
  charts.time = new Chart(tmCtx, {
    type: "line",
    data: {
      labels: history.map(h => `Test ${h.test_number}`),
      datasets: [{
        label: "Avg Time (s)",
        data: history.map(h => h.avg_time),
        borderColor: "#00D4FF", backgroundColor: "rgba(0,212,255,0.10)",
        tension: 0.4, fill: true, pointBackgroundColor: "#00D4FF", pointRadius: 5,
      }],
    },
    options: { ...CHART_DEFAULTS, responsive: true, maintainAspectRatio: false },
  });
}

document.getElementById("refresh-dashboard-btn").addEventListener("click", loadDashboard);

// Sync student ID header label
document.getElementById("student-id-input").addEventListener("input", () => {
  document.getElementById("hdr-student-id").textContent =
    document.getElementById("student-id-input").value || "1";
});
