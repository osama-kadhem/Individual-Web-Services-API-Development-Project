'use strict';

const API = '/api/v1';
const API_KEY = 'ironmind_secret_2026';
let currentView = 'dashboard';

// Helpers

/** Deterministic hue from a string (for avatar colours). */
function strHue(str) {
    let h = 0;
    for (const c of str) h = (h * 31 + c.charCodeAt(0)) & 0xffff;
    return h % 360;
}

/**
 * Extract a human-readable error message from any API response body.
 * Supports both standard error envelopes and older detail formats.
 */
function extractError(body) {
    return body?.error?.message ?? body?.detail ?? 'Unknown error';
}

/** Sport → CSS class + icon */
function sportBadge(sport = '') {
    const s = sport.toLowerCase();
    if (s.includes('run')) return { cls: 'run', icon: 'fa-person-running', label: sport };
    if (s.includes('bike') || s.includes('cycl')) return { cls: 'bike', icon: 'fa-bicycle', label: sport };
    if (s.includes('swim')) return { cls: 'swim', icon: 'fa-person-swimming', label: sport };
    return { cls: 'other', icon: 'fa-dumbbell', label: sport };
}

function renderSportBadge(sport) {
    const { cls, icon, label } = sportBadge(sport);
    return `<span class="sport-badge ${cls}"><i class="fa-solid ${icon}"></i> ${label}</span>`;
}

function renderAvatar(name) {
    const hue = strHue(name);
    const style = `background: linear-gradient(135deg, hsl(${hue},65%,40%), hsl(${(hue + 50) % 360},65%,50%));`;
    return `<div class="avatar" style="${style}">${name.charAt(0).toUpperCase()}</div>`;
}

function fmtDate(raw) {
    if (!raw) return '–';
    return new Date(raw).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function readinessBandClass(band = '') {
    return band.toLowerCase(); // 'high' | 'medium' | 'low'
}

// Initialisation

// Auth Logic
function validateKey() {
    const input = document.getElementById('access-key-input').value;
    const errorMsg = document.getElementById('auth-error');

    if (input === API_KEY) {
        document.getElementById('login-page').classList.add('login-fade-out');
        document.querySelector('.app-container').style.display = 'flex';
        sessionStorage.setItem('ironmind_auth', 'true');

        // Remove login page from DOM after fade animation
        setTimeout(() => {
            document.getElementById('login-page').remove();
        }, 600);

        initApp();
    } else {
        errorMsg.style.display = 'block';
        document.getElementById('access-key-input').value = '';
    }
}

// Global initialization logic split from DOMContentLoaded
async function initApp() {
    await Promise.all([
        fetchStats(),
        showView('dashboard')
    ]);
    document.getElementById('generic-form').addEventListener('submit', handleFormSubmit);
}

document.addEventListener('DOMContentLoaded', () => {
    // Check if previously authenticated in this session
    if (sessionStorage.getItem('ironmind_auth') === 'true') {
        const loginPage = document.getElementById('login-page');
        if (loginPage) loginPage.remove();
        document.querySelector('.app-container').style.display = 'flex';
        initApp();
    }

    // Add enter key listener for login
    document.getElementById('access-key-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') validateKey();
    });
});

// Navigation

const VIEW_META = {
    dashboard: { title: 'Dashboard', sub: 'Training overview and analytics' },
    athletes: { title: 'Athletes', sub: 'Manage your racing team' },
    sessions: { title: 'Training Sessions', sub: 'Historical workout performance' },
    sleep: { title: 'Sleep Logs', sub: 'Recovery and sleep metrics' },
    checkins: { title: 'Daily Check-ins', sub: 'Athlete readiness and well-being' },
    insights: { title: 'Training Insights', sub: 'Performance and readiness analysis' },
    docs: { title: 'API Console', sub: 'Interactive developer documentation' },
};

function showView(view) {
    currentView = view;

    // Highlight active nav item
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const navEl = document.getElementById(`nav-${view}`);
    if (navEl) navEl.classList.add('active');

    const { title, sub } = VIEW_META[view] ?? { title: view, sub: '' };
    document.getElementById('view-title').textContent = title;
    document.getElementById('view-subtitle').textContent = sub;

    const dataContainer = document.getElementById('data-container');
    const docsView = document.getElementById('docs-view');
    const statsSection = document.getElementById('stats-section');
    const addBtn = document.getElementById('add-btn');

    if (view === 'docs') {
        dataContainer.style.display = 'none';
        docsView.style.display = 'block';
        statsSection.style.display = 'none';
        return;
    }

    dataContainer.style.display = 'block';
    docsView.style.display = 'none';
    statsSection.style.display = 'grid';
    addBtn.style.display = view === 'insights' ? 'none' : '';

    document.getElementById('container-title').textContent =
        view === 'dashboard' ? 'Recent Athletes' : `Manage ${title}`;

    if (view === 'insights') {
        renderInsightsPlaceholder();
    } else {
        fetchData(view);
    }
}

// Stats

async function fetchStats() {
    try {
        const [athletes, sessions, checkins] = await Promise.all([
            fetch(`${API}/athletes/`, { headers: { 'X-API-KEY': API_KEY } }).then(r => r.json()),
            fetch(`${API}/sessions/`, { headers: { 'X-API-KEY': API_KEY } }).then(r => r.json()),
            fetch(`${API}/checkins/`, { headers: { 'X-API-KEY': API_KEY } }).then(r => r.json()),
        ]);

        document.getElementById('count-athletes').textContent = Array.isArray(athletes) ? athletes.length : '–';
        document.getElementById('count-sessions').textContent = Array.isArray(sessions) ? sessions.length : '–';

        if (Array.isArray(checkins) && checkins.length > 0) {
            const scores = checkins.map(c => c.readiness_score).filter(Boolean);
            const avg = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
            document.getElementById('avg-readiness').textContent = avg ? `${avg}%` : '–';
        }
    } catch (e) {
        console.error('Stats error:', e);
    }
}

// Data fetching

async function fetchData(view) {
    const body = document.getElementById('table-body');
    body.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:2rem;color:var(--text-muted)">
        <i class="fa-solid fa-spinner fa-spin"></i> Loading…</td></tr>`;

    const endpoint = view === 'sleep' ? 'sleep-logs' : (view === 'dashboard' ? 'athletes' : view);

    try {
        const data = await fetch(`${API}/${endpoint}/`, { headers: { 'X-API-KEY': API_KEY } }).then(r => r.json());
        if (!Array.isArray(data)) throw new Error(extractError(data));
        renderTable(view === 'dashboard' ? 'athletes' : view, data);
    } catch (e) {
        body.innerHTML = `<tr><td colspan="10" style="text-align:center;color:var(--red);padding:2rem">
            <i class="fa-solid fa-triangle-exclamation"></i> ${e.message}</td></tr>`;
    }
}

// Table rendering

const TABLE_HEADERS = {
    athletes: ['#', 'Athlete', 'Email', 'Age', ''],
    sessions: ['Athlete', 'Sport', 'Duration', 'Distance', 'Intensity', 'Date'],
    sleep: ['Athlete', 'Date', 'Sleep', 'Quality'],
    checkins: ['Athlete', 'Date', 'Fatigue', 'Stress', 'Mood', 'Soreness'],
};

function renderTable(view, data) {
    const head = document.getElementById('table-headers');
    const body = document.getElementById('table-body');

    head.innerHTML = (TABLE_HEADERS[view] ?? [])
        .map(h => `<th>${h}</th>`).join('');

    if (!data.length) {
        body.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:3rem;color:var(--text-muted)">
            <i class="fa-regular fa-folder-open"></i> No records found</td></tr>`;
        return;
    }

    body.innerHTML = data.map(item => `<tr class="fade-in">${rowHtml(view, item)}</tr>`).join('');
}

function rowHtml(view, item) {
    switch (view) {
        case 'athletes':
            return `
                <td style="color:var(--text-muted);font-size:0.85rem">#${item.id}</td>
                <td><div class="athlete-name">${renderAvatar(item.name)} ${item.name}</div></td>
                <td style="color:var(--text-muted)">${item.email}</td>
                <td>${item.age ?? '–'}</td>
                <td>
                    <button onclick="deleteItem('athletes',${item.id})"
                        style="background:none;border:none;cursor:pointer;color:var(--red);font-size:1rem"
                        title="Delete athlete">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>`;

        case 'sessions':
            return `
                <td style="color:var(--text-muted)">#${item.athlete_id}</td>
                <td>${renderSportBadge(item.sport)}</td>
                <td>${item.duration}<small style="color:var(--text-muted)"> min</small></td>
                <td>${item.distance ?? 0}<small style="color:var(--text-muted)"> km</small></td>
                <td>
                    <span style="color:${item.intensity >= 8 ? 'var(--red)' : item.intensity >= 5 ? 'var(--amber)' : 'var(--green)'}">
                        ${item.intensity ?? '–'}<small style="color:var(--text-muted)">/10</small>
                    </span>
                </td>
                <td style="color:var(--text-muted)">${fmtDate(item.date)}</td>`;

        case 'sleep':
            return `
                <td style="color:var(--text-muted)">#${item.athlete_id}</td>
                <td style="color:var(--text-muted)">${fmtDate(item.date)}</td>
                <td>${item.sleep_hours}<small style="color:var(--text-muted)">h</small></td>
                <td><span style="color:${item.sleep_quality >= 4 ? 'var(--green)' : item.sleep_quality >= 2 ? 'var(--amber)' : 'var(--red)'}">
                    ${'★'.repeat(item.sleep_quality ?? 0)}${'☆'.repeat(5 - (item.sleep_quality ?? 0))}
                </span></td>`;

        case 'checkins':
            return `
                <td style="color:var(--text-muted)">#${item.athlete_id}</td>
                <td style="color:var(--text-muted)">${fmtDate(item.date)}</td>
                ${['fatigue', 'stress', 'mood', 'soreness'].map(k =>
                `<td><span style="color:${item[k] >= 7 ? 'var(--red)' : item[k] >= 4 ? 'var(--amber)' : 'var(--green)'}">${item[k]}</span><small style="color:var(--text-muted)">/10</small></td>`
            ).join('')}`;

        default: return '';
    }
}

// Insights panel

function renderInsightsPlaceholder() {
    const head = document.getElementById('table-headers');
    const body = document.getElementById('table-body');
    head.innerHTML = '';
    body.innerHTML = `
        <tr>
            <td colspan="10" style="padding:2.5rem;text-align:center">
                <h3 style="margin-bottom:.5rem">Analyze Athlete Readiness</h3>
                <p style="color:var(--text-muted);margin-bottom:1.5rem">
                    Enter an athlete ID to generate a real-time readiness report.
                </p>
                <div style="display:flex;gap:10px;justify-content:center">
                    <input id="insight-athlete-id" type="number" placeholder="Athlete ID (e.g. 1)"
                        style="width:200px;padding:10px 14px;border-radius:10px;
                                background:rgba(255,255,255,0.05);border:1px solid var(--glass-border);color:white;outline:none">
                    <button class="btn-primary" onclick="loadAthleteInsights()">
                        <i class="fa-solid fa-bolt"></i> Generate Report
                    </button>
                </div>
                <div id="insights-result" style="margin-top:2rem"></div>
            </td>
        </tr>`;
}

async function loadAthleteInsights() {
    const athleteId = document.getElementById('insight-athlete-id')?.value;
    if (!athleteId) return alert('Please enter an Athlete ID');

    const result = document.getElementById('insights-result');
    result.innerHTML = `<p style="color:var(--text-muted)"><i class="fa-solid fa-spinner fa-spin"></i> Analyzing…</p>`;

    try {
        const [readiness, trends] = await Promise.all([
            fetch(`${API}/athletes/${athleteId}/insights/readiness`, { headers: { 'X-API-KEY': API_KEY } }).then(r => r.json()),
            fetch(`${API}/athletes/${athleteId}/analytics/trends`, { headers: { 'X-API-KEY': API_KEY } }).then(r => r.json()),
        ]);

        if (readiness.error) throw new Error(readiness.error.message);
        renderInsightsDashboard(readiness, trends);
    } catch (e) {
        result.innerHTML = `<p style="color:var(--red)"><i class="fa-solid fa-circle-exclamation"></i> ${e.message}</p>`;
    }
}

function renderInsightsDashboard(readiness, trends) {
    const result = document.getElementById('insights-result');
    const band = readiness.readiness_band;
    const cls = readinessBandClass(band);

    const reasonsHtml = readiness.top_reasons.map(r => `
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 14px;background:rgba(255,255,255,0.02);border-radius:10px;margin-bottom:8px">
            <span style="color:var(--text-muted);font-size:.9rem">${r.reason}</span>
            <span style="font-weight:700;color:${r.impact > 0 ? 'var(--green)' : 'var(--red)'}">
                ${r.impact > 0 ? '+' : ''}${r.impact} pts
            </span>
        </div>`).join('');

    result.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;text-align:left">

            <!-- Score card -->
            <div class="stat-card" style="display:flex;flex-direction:column;align-items:flex-start;gap:.5rem">
                <div class="readiness-ring ${cls}">${readiness.readiness_score}</div>
                <div style="font-size:1.1rem;font-weight:700">${band} Readiness</div>
                <div style="font-size:.85rem;color:var(--text-muted);margin-bottom:.5rem">${readiness.date}</div>
                <div style="width:100%">
                    <p style="font-weight:600;margin-bottom:.6rem;font-size:.9rem">Impact Factors</p>
                    ${reasonsHtml}
                </div>
            </div>

            <!-- Signals card -->
            <div class="stat-card">
                <p style="color:var(--text-muted);margin-bottom:1rem;font-weight:600;font-size:.9rem">Training Signals</p>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-bottom:1.25rem">
                    ${[
            ['ACWR', readiness.signals.acwr, 'Optimal: 0.8–1.3'],
            ['7d Load', readiness.signals.acute_load_7d, 'Acute workload'],
            ['Sleep', readiness.signals.sleep_hours + 'h', 'Duration'],
            ['Sleep Qual', readiness.signals.sleep_quality + '/5', 'Quality'],
        ].map(([label, val, hint]) => `
                        <div style="background:rgba(0,0,0,0.2);padding:14px;border-radius:12px">
                            <small style="color:var(--text-muted)">${label}</small>
                            <div style="font-size:1.4rem;font-weight:700;margin:4px 0">${val}</div>
                            <small style="color:var(--text-muted);font-size:.75rem">${hint}</small>
                        </div>`).join('')}
                </div>
                <button class="btn-primary" style="width:100%;justify-content:center"
                    onclick="openWhatIfModal(${readiness.athlete_id})">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Try What-If Simulator
                </button>
            </div>
        </div>`;
}

// What-If modal

function openWhatIfModal(athleteId) {
    const modal = document.getElementById('modal');
    const fields = document.getElementById('form-fields');

    document.getElementById('modal-title').textContent = 'What-If Simulator';
    document.getElementById('modal-subtitle').textContent = 'Project how tonight\'s plan affects your readiness.';
    modal.style.display = 'flex';

    fields.innerHTML = `
        <input type="hidden" name="athlete_id" value="${athleteId}">
        <div class="form-group"><label>Planned duration (min)</label>
            <input type="number" name="planned_session_duration" value="60" min="1" required></div>
        <div class="form-group"><label>Planned intensity (1–10 RPE)</label>
            <input type="number" name="planned_session_intensity" value="7" min="1" max="10" required></div>
        <div class="form-group"><label>Expected sleep (hours)</label>
            <input type="number" name="expected_sleep_hours" step="0.5" value="8" min="0" max="24" required></div>
        <div class="form-group"><label>Expected sleep quality (1–5)</label>
            <input type="number" name="expected_sleep_quality" value="4" min="1" max="5" required></div>`;

    const form = document.getElementById('generic-form');
    form.onsubmit = async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(e.target));
        ['planned_session_duration', 'planned_session_intensity', 'expected_sleep_hours', 'expected_sleep_quality']
            .forEach(k => { data[k] = parseFloat(data[k]); });

        try {
            const res = await fetch(`${API}/athletes/${athleteId}/whatif/readiness`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': API_KEY
                },
                body: JSON.stringify(data),
            }).then(r => r.json());

            if (res.error) throw new Error(res.error.message);

            alert(`${res.change_description}\n\nProjected score: ${res.projected_readiness.readiness_score} (${res.projected_readiness.readiness_band})`);
            closeModal();
            loadAthleteInsights();
        } catch (err) {
            alert(`Simulation failed: ${err.message}`);
        }
    };
}

// CRUD modal

const TODAY = new Date().toISOString().split('T')[0];

const MODAL_CONFIGS = {
    athletes: {
        title: 'Register Athlete',
        subtitle: 'Create a new athlete profile',
        fields: `
            <div class="form-group"><label>Full Name</label>
                <input type="text" name="name" required placeholder="e.g. Jane Doe"></div>
            <div class="form-group"><label>Email Address</label>
                <input type="email" name="email" required placeholder="jane@ironmind.com"></div>
            <div class="form-group"><label>Age (optional)</label>
                <input type="number" name="age" min="10" max="100" placeholder="28"></div>`,
    },
    sessions: {
        title: 'Log Session',
        subtitle: 'Record a completed training session',
        fields: `
            <div class="form-group"><label>Athlete ID</label>
                <input type="number" name="athlete_id" required></div>
            <div class="form-group"><label>Sport</label>
                <select name="sport">
                    <option>Swimming</option><option>Cycling</option><option>Running</option>
                </select>
            </div>
            <div class="form-group"><label>Duration (min) — must be > 0</label>
                <input type="number" name="duration" required min="1"></div>
            <div class="form-group"><label>Distance (km, optional)</label>
                <input type="number" step="0.1" name="distance" min="0"></div>
            <div class="form-group"><label>Intensity — RPE 1–10</label>
                <input type="number" name="intensity" min="1" max="10"></div>`,
    },
    sleep: {
        title: 'Log Sleep',
        subtitle: 'Log sleep for an athlete',
        fields: `
            <div class="form-group"><label>Athlete ID</label>
                <input type="number" name="athlete_id" required></div>
            <div class="form-group"><label>Date</label>
                <input type="date" name="date" value="${TODAY}"></div>
            <div class="form-group"><label>Sleep Hours (0–24)</label>
                <input type="number" step="0.5" name="sleep_hours" required min="0" max="24"></div>
            <div class="form-group"><label>Quality (1–5)</label>
                <input type="number" name="sleep_quality" min="1" max="5"></div>`,
    },
    checkins: {
        title: 'Daily Check-in',
        subtitle: 'Log a wellness check-in',
        fields: `
            <div class="form-group"><label>Athlete ID</label>
                <input type="number" name="athlete_id" required></div>
            <div class="form-group"><label>Date</label>
                <input type="date" name="date" value="${TODAY}"></div>
            <div class="form-group"><label>Fatigue (1–10)</label>
                <input type="number" name="fatigue" required min="1" max="10"></div>
            <div class="form-group"><label>Stress (1–10)</label>
                <input type="number" name="stress" required min="1" max="10"></div>
            <div class="form-group"><label>Mood (1–10)</label>
                <input type="number" name="mood" required min="1" max="10"></div>
            <div class="form-group"><label>Soreness (1–10)</label>
                <input type="number" name="soreness" required min="1" max="10"></div>`,
    },
};

function openModal() {
    const key = currentView === 'dashboard' ? 'athletes' : currentView;
    const config = MODAL_CONFIGS[key];
    if (!config) return;

    document.getElementById('modal-title').textContent = config.title;
    document.getElementById('modal-subtitle').textContent = config.subtitle;
    document.getElementById('form-fields').innerHTML = config.fields;
    document.getElementById('generic-form').onsubmit = handleFormSubmit;
    document.getElementById('modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
    document.getElementById('generic-form').onsubmit = handleFormSubmit;
}

// Form submit

const NUMERIC_KEYS = new Set([
    'athlete_id', 'duration', 'distance', 'intensity',
    'sleep_hours', 'sleep_quality', 'fatigue', 'stress', 'mood', 'soreness', 'age',
]);

async function handleFormSubmit(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    for (const k of Object.keys(data)) {
        if (NUMERIC_KEYS.has(k) && data[k] !== '') data[k] = parseFloat(data[k]);
    }

    const view = currentView === 'dashboard' ? 'athletes' : currentView;
    let url = `${API}/${view === 'sleep' ? 'sleep-logs' : view}/`;

    if (view === 'sleep' && data.athlete_id)
        url = `${API}/athletes/${data.athlete_id}/sleep`;
    else if (view === 'checkins' && data.athlete_id)
        url = `${API}/athletes/${data.athlete_id}/checkins`;

    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': API_KEY
            },
            body: JSON.stringify(data)
        });
        const body = await res.json();

        if (!res.ok) throw new Error(extractError(body));

        closeModal();
        fetchStats();
        showView(currentView);
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

// Delete

async function deleteItem(type, id) {
    if (!confirm('Delete this record? This cannot be undone.')) return;
    const endpoint = type === 'sleep' ? 'sleep-logs' : type;

    try {
        const res = await fetch(`${API}/${endpoint}/${id}`, {
            method: 'DELETE',
            headers: { 'X-API-KEY': API_KEY }
        });
        if (!res.ok) {
            const body = await res.json();
            throw new Error(extractError(body));
        }
        fetchStats();
        showView(currentView);
    } catch (err) {
        alert(`Delete failed: ${err.message}`);
    }
}
