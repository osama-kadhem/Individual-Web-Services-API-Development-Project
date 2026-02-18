const API_URL = '/api/v1';
let currentView = 'dashboard';

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    showView('dashboard');

    // Form submission
    document.getElementById('generic-form').addEventListener('submit', handleFormSubmit);
});

// View Management
async function showView(view) {
    currentView = view;

    // Update Active Nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.innerText.toLowerCase().includes(view)) {
            item.classList.add('active');
        }
    });

    // Update Titles
    const titles = {
        'dashboard': { title: 'Dashboard', sub: 'Training overview and analytics' },
        'athletes': { title: 'Athletes', sub: 'Manage your racing team' },
        'sessions': { title: 'Training Sessions', sub: 'Historical workout performance' },
        'sleep': { title: 'Sleep Logs', sub: 'Recovery and sleep metrics' },
        'checkins': { title: 'Daily Check-ins', sub: 'Athlete readiness and well-being' },
        'docs': { title: 'API Console', sub: 'Interactive developer documentation' }
    };

    document.getElementById('view-title').innerText = titles[view].title;
    document.getElementById('view-subtitle').innerText = titles[view].sub;

    const dataContainer = document.getElementById('data-container');
    const docsView = document.getElementById('docs-view');

    if (view === 'docs') {
        dataContainer.style.display = 'none';
        docsView.style.display = 'block';
        document.getElementById('stats-section').style.display = 'none';
    } else {
        dataContainer.style.display = 'block';
        docsView.style.display = 'none';
        document.getElementById('stats-section').style.display = 'grid';
        document.getElementById('container-title').innerText = `Manage ${view.charAt(0).toUpperCase() + view.slice(1)}`;

        if (view === 'dashboard') {
            fetchRecentActivity();
        } else {
            fetchData(view);
        }
    }
}

// Stats Fetching
async function fetchStats() {
    try {
        const athletes = await fetch(`${API_URL}/athletes/`).then(r => r.json());
        const sessions = await fetch(`${API_URL}/sessions/`).then(r => r.json());
        const checkins = await fetch(`${API_URL}/checkins/`).then(r => r.json());

        document.getElementById('count-athletes').innerText = athletes.length;
        document.getElementById('count-sessions').innerText = sessions.length;

        if (checkins.length > 0) {
            const avg = checkins.reduce((acc, curr) => acc + curr.readiness_score, 0) / checkins.length;
            document.getElementById('avg-readiness').innerText = `${Math.round(avg || 0)}%`;
        }
    } catch (e) {
        console.error('Stats error:', e);
    }
}

// Data Fetching
async function fetchData(view) {
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '<tr><td colspan="10" style="text-align:center">Loading...</td></tr>';

    const endpoint = view === 'sleep' ? 'sleep-logs' : view;

    try {
        const data = await fetch(`${API_URL}/${endpoint}/`).then(r => r.json());
        renderTable(view, data);
    } catch (e) {
        tableBody.innerHTML = '<tr><td colspan="10" style="text-align:center; color: red">Failed to load data</td></tr>';
    }
}

function renderTable(view, data) {
    const head = document.getElementById('table-headers');
    const body = document.getElementById('table-body');
    head.innerHTML = '';
    body.innerHTML = '';

    if (!data || data.length === 0) {
        body.innerHTML = '<tr><td colspan="10" style="text-align:center">No records found</td></tr>';
        return;
    }

    const configs = {
        'athletes': ['ID', 'Name', 'Email', 'Age', 'Actions'],
        'sessions': ['Athlete ID', 'Sport', 'Duration', 'Distance', 'Intensity', 'Date'],
        'sleep': ['Athlete ID', 'Date', 'Sleep Hours', 'Quality (1-5)'],
        'checkins': ['Athlete ID', 'Date', 'Fatigue', 'Stress', 'Mood', 'Soreness']
    };

    configs[view].forEach(h => {
        const th = document.createElement('th');
        th.innerText = h;
        head.appendChild(th);
    });

    data.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = 'fade-in';

        let html = '';
        if (view === 'athletes') {
            html = `
                <td>#${item.id}</td>
                <td><div class="athlete-name"><div class="avatar">${item.name.charAt(0)}</div> ${item.name}</div></td>
                <td>${item.email}</td>
                <td>${item.age || 'N/A'}</td>
                <td><i class="fa-solid fa-trash" style="color: #EF4444; cursor:pointer" onclick="deleteItem('athletes', ${item.id})"></i></td>
            `;
        } else if (view === 'sessions') {
            html = `<td>${item.athlete_id}</td><td>${item.sport}</td><td>${item.duration}m</td><td>${item.distance || 0}km</td><td>${item.intensity}/10</td><td>${new Date(item.date).toLocaleDateString()}</td>`;
        } else if (view === 'sleep') {
            html = `<td>${item.athlete_id}</td><td>${new Date(item.date).toLocaleDateString()}</td><td>${item.sleep_hours}h</td><td>${item.sleep_quality}/5</td>`;
        } else if (view === 'checkins') {
            html = `<td>${item.athlete_id}</td><td>${new Date(item.date).toLocaleDateString()}</td><td>${item.fatigue}/10</td><td>${item.stress}/10</td><td>${item.mood}/10</td><td>${item.soreness}/10</td>`;
        }

        tr.innerHTML = html;
        body.appendChild(tr);
    });
}

// Modal Management
function openModal() {
    const modal = document.getElementById('modal');
    const fields = document.getElementById('form-fields');
    const title = document.getElementById('modal-title');
    modal.style.display = 'flex';
    fields.innerHTML = '';

    if (currentView === 'athletes' || currentView === 'dashboard') {
        title.innerText = 'Register Athlete';
        fields.innerHTML = `
            <div class="form-group"><label>Full Name</label><input type="text" name="name" required placeholder="John Doe"></div>
            <div class="form-group"><label>Email Address</label><input type="email" name="email" required placeholder="john@ironman.com"></div>
            <div class="form-group"><label>Age</label><input type="number" name="age" placeholder="30"></div>
        `;
    } else if (currentView === 'sessions') {
        title.innerText = 'Log Session';
        fields.innerHTML = `
            <div class="form-group"><label>Athlete ID</label><input type="number" name="athlete_id" required></div>
            <div class="form-group"><label>Sport</label><select name="sport"><option>Swimming</option><option>Cycling</option><option>Running</option></select></div>
            <div class="form-group"><label>Duration (min)</label><input type="number" name="duration" required></div>
            <div class="form-group"><label>Distance (km)</label><input type="number" step="0.1" name="distance"></div>
            <div class="form-group"><label>Intensity (1-10)</label><input type="number" name="intensity" min="1" max="10"></div>
        `;
    } else if (currentView === 'sleep') {
        title.innerText = 'Log Sleep';
        fields.innerHTML = `
            <div class="form-group"><label>Athlete ID</label><input type="number" name="athlete_id" required></div>
            <div class="form-group"><label>Date</label><input type="date" name="date" value="${new Date().toISOString().split('T')[0]}"></div>
            <div class="form-group"><label>Sleep Hours (0-24)</label><input type="number" step="0.1" name="sleep_hours" required min="0" max="24"></div>
            <div class="form-group"><label>Quality (1-5)</label><input type="number" name="sleep_quality" required min="1" max="5"></div>
        `;
    } else if (currentView === 'checkins') {
        title.innerText = 'Daily Check-in';
        fields.innerHTML = `
            <div class="form-group"><label>Athlete ID</label><input type="number" name="athlete_id" required></div>
            <div class="form-group"><label>Date</label><input type="date" name="date" value="${new Date().toISOString().split('T')[0]}"></div>
            <div class="form-group"><label>Fatigue (1-10)</label><input type="number" name="fatigue" required min="1" max="10"></div>
            <div class="form-group"><label>Stress (1-10)</label><input type="number" name="stress" required min="1" max="10"></div>
            <div class="form-group"><label>Mood (1-10)</label><input type="number" name="mood" required min="1" max="10"></div>
            <div class="form-group"><label>Soreness (1-10)</label><input type="number" name="soreness" required min="1" max="10"></div>
        `;
    }
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Fix numeric types
    for (const key in data) {
        if (['athlete_id', 'duration', 'distance', 'intensity', 'sleep_hours', 'sleep_quality', 'fatigue', 'stress', 'mood', 'soreness'].includes(key)) {
            data[key] = parseFloat(data[key]);
        }
    }

    const endpoint = currentView === 'dashboard' ? 'athletes' : currentView;
    let finalEndpoint = endpoint === 'sleep' ? 'sleep-logs' : endpoint;
    let url = `${API_URL}/${finalEndpoint}/`;

    // Phase 4: Use nested endpoints for Sleep/Checkins if athlete_id is present
    if (currentView === 'sleep' && data.athlete_id) {
        url = `${API_URL}/athletes/${data.athlete_id}/sleep`;
    } else if (currentView === 'checkins' && data.athlete_id) {
        url = `${API_URL}/athletes/${data.athlete_id}/checkins`;
    }

    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            closeModal();
            fetchStats();
            showView(currentView);
        } else {
            const err = await res.json();
            alert(`Error: ${err.detail || 'Failed to save'}`);
        }
    } catch (e) {
        alert('Error connecting to API');
    }
}

async function deleteItem(type, id) {
    if (!confirm('Are you sure you want to delete this?')) return;
    const finalType = type === 'sleep' ? 'sleep-logs' : type;

    try {
        await fetch(`${API_URL}/${finalType}/${id}`, { method: 'DELETE' });
        fetchStats();
        showView(currentView);
    } catch (e) {
        alert('Delete failed');
    }
}

async function fetchRecentActivity() {
    fetchData('athletes');
}
