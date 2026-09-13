const API_BASE = 'http://localhost:8050/api';

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initForm();
    initChat();
    loadDashboardData();
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('page-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');

            navItems.forEach(n => n.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));

            item.classList.add('active');
            document.getElementById(`tab-${targetTab}`).classList.add('active');

            if (targetTab === 'dashboard') {
                pageTitle.textContent = 'Panel de Control GEO & Indexación Exprés';
                loadDashboardData();
            } else if (targetTab === 'chat-engine') {
                pageTitle.textContent = 'Chatbot IA EXPRESS · Motor 2 de Recomendación Instantánea (1s)';
            } else if (targetTab === 'new-business') {
                pageTitle.textContent = 'Alta de Nuevo Negocio para Indexación Exprés';
            } else if (targetTab === 'index-jobs') {
                pageTitle.textContent = 'Historial de Pings al Protocolo IndexNow';
                loadIndexJobs();
            }
        });
    });
}

async function loadDashboardData() {
    try {
        const res = await fetch(`${API_BASE}/business`);
        const businesses = await res.json();

        document.getElementById('stat-count').textContent = businesses.length;

        const jobsRes = await fetch(`${API_BASE}/index-jobs`);
        const jobs = await jobsRes.json();
        document.getElementById('stat-index-count').textContent = jobs.length;

        renderBusinessList(businesses);
    } catch (err) {
        console.error("Error cargando dashboard:", err);
    }
}

function renderBusinessList(businesses) {
    const container = document.getElementById('business-list');
    container.innerHTML = '';

    if (businesses.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay negocios registrados aún. ¡Registra uno en la pestaña Alta de Negocio!</p>';
        return;
    }

    businesses.forEach(b => {
        const card = document.createElement('div');
        card.className = 'business-card';

        const siteUrl = `http://localhost:8050/sites/${b.slug}/index.html`;

        card.innerHTML = `
            <h4>${escapeHtml(b.name)}</h4>
            <p class="business-meta">📍 ${escapeHtml(b.town)}, ${escapeHtml(b.province)} | 🏢 ${escapeHtml(b.category)}</p>
            <p>${escapeHtml(b.description)}</p>
            <p class="business-meta"><strong>Especialidades:</strong> ${escapeHtml(b.specialties || 'General')}</p>
            
            <div class="card-actions">
                <a href="${siteUrl}" target="_blank" class="btn btn-secondary text-cyan">🌐 Ver Página RAG</a>
                <button class="btn btn-secondary" onclick="viewSchema(${b.id})">🏷️ Schema.org</button>
                <button class="btn btn-primary" onclick="triggerIndexNow(${b.id})">⚡ Disparar IndexNow</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function viewSchema(businessId) {
    try {
        const res = await fetch(`${API_BASE}/business/${businessId}/content`);
        const contents = await res.json();
        if (contents.length > 0) {
            document.getElementById('schema-code').textContent = contents[0].schema_jsonld;
            document.getElementById('modal-schema').classList.add('active');
        } else {
            alert("No hay esquema generado.");
        }
    } catch (err) {
        alert("Error al cargar esquema JSON-LD.");
    }
}

function closeModal() {
    document.getElementById('modal-schema').classList.remove('active');
}

async function triggerIndexNow(businessId) {
    try {
        const res = await fetch(`${API_BASE}/index-now/${businessId}`, {
            method: 'POST'
        });
        const job = await res.json();

        alert(`🚀 IndexNow Disparado con Éxito!\n\nEstado: ${job.indexnow_status.toUpperCase()}\nCódigo HTTP: ${job.http_status_code}\nURL Enviada: ${job.target_url}`);
        loadDashboardData();
    } catch (err) {
        alert("Error al enviar ping a IndexNow.");
    }
}

async function loadIndexJobs() {
    try {
        const res = await fetch(`${API_BASE}/index-jobs`);
        const jobs = await res.json();
        const tbody = document.getElementById('jobs-list');
        tbody.innerHTML = '';

        jobs.forEach(j => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${j.id}</td>
                <td><a href="${j.target_url}" target="_blank" style="color:#38bdf8;">${escapeHtml(j.target_url)}</a></td>
                <td><span style="color:#34d399; font-weight:600;">⚡ ${escapeHtml(j.indexnow_status.toUpperCase())}</span></td>
                <td>${j.http_status_code || 200}</td>
                <td>${new Date(j.submitted_at).toLocaleString('es-ES')}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error al cargar historial:", err);
    }
}

function initForm() {
    const form = document.getElementById('business-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            name: document.getElementById('name').value,
            category: document.getElementById('category').value,
            town: document.getElementById('town').value,
            province: document.getElementById('province').value || "Sevilla",
            address: document.getElementById('address').value,
            latitude: parseFloat(document.getElementById('latitude').value) || 37.3712,
            longitude: parseFloat(document.getElementById('longitude').value) || -6.0715,
            phone: document.getElementById('phone').value,
            website: document.getElementById('website').value,
            specialties: document.getElementById('specialties').value,
            description: document.getElementById('description').value,
        };

        try {
            const res = await fetch(`${API_BASE}/business`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                const business = await res.json();

                // Disparar IndexNow automáticamente al crear
                await fetch(`${API_BASE}/index-now/${business.id}`, { method: 'POST' });

                alert(`🎉 Negocio "${business.name}" registrado!\n\nSe ha generado la landing con Marcado JSON-LD Schema.org y se ha enviado la notificación exprés a IndexNow (Bing & Perplexity).`);

                form.reset();
                document.querySelector('[data-tab="dashboard"]').click();
            } else {
                alert("Error al registrar negocio.");
            }
        } catch (err) {
            alert("Error de conexión al servidor.");
        }
    });
}

function initChat() {
    const chatForm = document.getElementById('chat-form');
    if (!chatForm) return;

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('chat-input');
        const msg = input.value.trim();
        if (!msg) return;

        input.value = '';
        await sendChatMessage(msg);
    });
}

function sendQuickPrompt(promptText) {
    document.getElementById('chat-input').value = promptText;
    sendChatMessage(promptText);
}

async function sendChatMessage(messageText) {
    const historyContainer = document.getElementById('chat-history');

    // Render User Bubble
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user-bubble';
    userBubble.textContent = messageText;
    historyContainer.appendChild(userBubble);
    historyContainer.scrollTop = historyContainer.scrollHeight;

    // Loading Bubble
    const loadingBubble = document.createElement('div');
    loadingBubble.className = 'chat-bubble bot-bubble';
    loadingBubble.innerHTML = '⚡ <em>Consultando base de datos RAG e inyectando reglas de contexto...</em>';
    historyContainer.appendChild(loadingBubble);
    historyContainer.scrollTop = historyContainer.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        });

        const data = await res.json();
        historyContainer.removeChild(loadingBubble);

        // Render Bot Response
        const botBubble = document.createElement('div');
        botBubble.className = 'chat-bubble bot-bubble';
        botBubble.innerHTML = formatMarkdownResponse(data.bot_response);
        historyContainer.appendChild(botBubble);
        historyContainer.scrollTop = historyContainer.scrollHeight;

        // Actualizar Inspector de System Prompt
        updateInspector(data);

    } catch (err) {
        historyContainer.removeChild(loadingBubble);
        const errorBubble = document.createElement('div');
        errorBubble.className = 'chat-bubble bot-bubble';
        errorBubble.textContent = '❌ Error al comunicarse con el Motor 2.';
        historyContainer.appendChild(errorBubble);
    }
}

function updateInspector(data) {
    document.getElementById('inspect-town').textContent = data.town_detected ? data.town_detected.toUpperCase() : 'Ninguno';
    document.getElementById('inspect-intent').textContent = data.intent_detected ? data.intent_detected.toUpperCase() : 'Ninguna';

    if (data.matched_business) {
        document.getElementById('inspect-business').textContent = `🎯 ${data.matched_business.name} (${data.matched_business.town})`;
    } else {
        document.getElementById('inspect-business').textContent = 'Sin coincidencia registrada';
    }

    document.getElementById('inspect-prompt').textContent = data.system_prompt_injected;
}

function formatMarkdownResponse(text) {
    if (!text) return '';
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

