let currentAlertId = null;
let statusUpdateInterval;
let missionStartTime = Date.now();

// Mission Time Clock
function updateMissionTime() {
    const elapsed = Date.now() - missionStartTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    document.getElementById('missionTime').textContent = 
        `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

setInterval(updateMissionTime, 1000);

// MediBot Functions
function toggleMedibot() {
    const window = document.getElementById('medibotWindow');
    window.classList.toggle('hidden');
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    const messagesDiv = document.getElementById('chatMessages');
    const userMsg = document.createElement('div');
    userMsg.className = 'message-user';
    userMsg.innerHTML = `
        <div class="text-xs text-slate-500 mb-1 text-right">Vous</div>
        <div class="bg-slate-800/50 rounded-lg p-3 text-sm inline-block">${message}</div>
    `;
    messagesDiv.appendChild(userMsg);
    
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Simulate bot response
    setTimeout(() => {
        const botMsg = document.createElement('div');
        botMsg.className = 'message-bot';
        botMsg.innerHTML = `
            <div class="text-xs text-slate-500 mb-1">MediBot</div>
            <div class="bg-slate-800/50 rounded-lg p-3 text-sm">Je traite votre demande...</div>
        `;
        messagesDiv.appendChild(botMsg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }, 1000);
}

// FAB Click Handler
document.getElementById('medibotFab').addEventListener('click', toggleMedibot);

function startDashboardUpdates() {
    // Check for active alerts every 5 seconds
    statusUpdateInterval = setInterval(checkForActiveAlerts, 5000);
    
    // Initial check
    checkForActiveAlerts();
    
    // Add agent log entries
    addAgentLog('Triage AI initialized');
    addAgentLog('Coordinator online');
    addAgentLog('Ambulance fleet ready');
}

function addAgentLog(message) {
    const logsDiv = document.getElementById('agentLogs');
    const time = new Date().toLocaleTimeString('fr-FR');
    const logLine = document.createElement('div');
    logLine.className = 'log-line';
    logLine.textContent = `[${time}] ${message}`;
    logsDiv.appendChild(logLine);
    
    // Keep only last 10 logs
    while (logsDiv.children.length > 10) {
        logsDiv.removeChild(logsDiv.firstChild);
    }
    
    logsDiv.scrollTop = logsDiv.scrollHeight;
}

async function checkForActiveAlerts() {
    try {
        const response = await fetch('/api/alerts/active');
        const data = await response.json();
        
        if (data.alert) {
            if (currentAlertId !== data.alert.id) {
                currentAlertId = data.alert.id;
                displayActiveAlert(data.alert);
                startAlertTracking(data.alert.id);
            }
        } else {
            clearActiveAlert();
        }
    } catch (error) {
        console.error('Error checking for active alerts:', error);
    }
}

function displayActiveAlert(alert) {
    const alertContainer = document.getElementById('currentAlert');
    
    alertContainer.innerHTML = `
        <div class="space-y-3">
            <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-600">Patient</span>
                <span class="text-sm text-gray-800">${alert.patient_name}</span>
            </div>
            <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-600">Âge</span>
                <span class="text-sm text-gray-800">${alert.age} ans</span>
            </div>
            <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-600">Gravité</span>
                <span class="px-2 py-1 text-xs rounded-full ${getSeverityClass(alert.severity)}">
                    ${getSeverityText(alert.severity)}
                </span>
            </div>
            <div class="pt-2 border-t">
                <span class="text-sm font-medium text-gray-600">Symptômes</span>
                <p class="text-sm text-gray-800 mt-1">${alert.symptoms}</p>
            </div>
            <div class="pt-2">
                <span class="text-sm font-medium text-gray-600">Statut</span>
                <div class="flex items-center mt-1">
                    <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
                    <span class="text-sm text-gray-800">${getStatusText(alert.status)}</span>
                </div>
            </div>
        </div>
    `;
}

function clearActiveAlert() {
    currentAlertId = null;
    const alertContainer = document.getElementById('currentAlert');
    
    alertContainer.innerHTML = `
        <div class="text-center text-gray-500 py-8">
            <i class="fas fa-clipboard-list text-4xl mb-3"></i>
            <p>Aucune alerte active</p>
        </div>
    `;
    
    // Clear map tracking
    if (window.mapFunctions) {
        window.mapFunctions.stopAmbulanceTracking();
        window.mapFunctions.stopETACountdown();
    }
    
    // Clear hospital info
    document.getElementById('hospitalInfo').innerHTML = `
        <div class="text-center text-gray-500 py-4">
            <i class="fas fa-hospital text-3xl mb-2"></i>
            <p>En attente d'assignation</p>
        </div>
    `;
}

async function startAlertTracking(alertId) {
    try {
        const response = await fetch(`/api/status/${alertId}`);
        const data = await response.json();
        
        if (data.route_data && window.mapFunctions) {
            window.mapFunctions.startAmbulanceTracking(data.route_data);
            
            if (data.eta_minutes) {
                window.mapFunctions.startETACountdown(data.eta_minutes);
            }
        }
        
        if (data.hospital) {
            displayHospitalInfo(data.hospital);
            
            if (window.mapFunctions) {
                window.mapFunctions.highlightDestinationHospital(data.hospital.name);
            }
        }
        
        // Update recent alerts table
        updateRecentAlertsTable();
        
    } catch (error) {
        console.error('Error starting alert tracking:', error);
    }
}

function displayHospitalInfo(hospital) {
    const hospitalContainer = document.getElementById('hospitalInfo');
    
    hospitalContainer.innerHTML = `
        <div class="space-y-3">
            <div class="flex items-center space-x-2">
                <i class="fas fa-hospital text-blue-600"></i>
                <h4 class="font-semibold text-gray-800">${hospital.name}</h4>
            </div>
            <div class="text-sm text-gray-600">
                <p><strong>Service:</strong> ${hospital.service}</p>
                <p><strong>Distance:</strong> ${hospital.distance_km} km</p>
            </div>
            <div class="pt-2 border-t">
                <div class="flex items-center text-green-600">
                    <i class="fas fa-bed mr-2"></i>
                    <span class="text-sm">Lit ${hospital.bed_number} réservé</span>
                </div>
            </div>
        </div>
    `;
}

async function updateRecentAlertsTable() {
    try {
        const response = await fetch('/api/alerts/recent');
        const data = await response.json();
        
        const tbody = document.getElementById('recentAlerts');
        
        if (data.alerts && data.alerts.length > 0) {
            tbody.innerHTML = data.alerts.map(alert => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${formatTime(alert.created_at)}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${alert.patient_name}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 text-xs rounded-full ${getSeverityClass(alert.severity)}">
                            ${getSeverityText(alert.severity)}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 text-xs rounded-full ${getStatusClass(alert.status)}">
                            ${getStatusText(alert.status)}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${alert.eta || '--'}
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="px-6 py-4 text-center text-gray-500">Aucune alerte récente</td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('Error updating recent alerts:', error);
    }
}

// Utility functions
function getSeverityClass(severity) {
    const classes = {
        1: 'bg-red-100 text-red-800',
        2: 'bg-orange-100 text-orange-800',
        3: 'bg-yellow-100 text-yellow-800',
        4: 'bg-blue-100 text-blue-800',
        5: 'bg-green-100 text-green-800'
    };
    return classes[severity] || 'bg-gray-100 text-gray-800';
}

function getSeverityText(severity) {
    const texts = {
        1: 'Critique',
        2: 'Urgent',
        3: 'Modéré',
        4: 'Mineur',
        5: 'Bénin'
    };
    return texts[severity] || 'Inconnu';
}

function getStatusClass(status) {
    const classes = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'assigned': 'bg-blue-100 text-blue-800',
        'en_route': 'bg-orange-100 text-orange-800',
        'arrived': 'bg-green-100 text-green-800',
        'completed': 'bg-gray-100 text-gray-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
}

function getStatusText(status) {
    const texts = {
        'pending': 'En attente',
        'assigned': 'Assigné',
        'en_route': 'En route',
        'arrived': 'Arrivé',
        'completed': 'Terminé'
    };
    return texts[status] || 'Inconnu';
}

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
});