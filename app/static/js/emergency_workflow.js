// Emergency Workflow Manager - Real-time status updates
class EmergencyWorkflowManager {
    constructor(alertId, mapInstance) {
        this.alertId = alertId;
        this.map = mapInstance;
        this.pollingInterval = null;
        this.currentRoute = null;
        this.statusCallbacks = [];
    }

    // Start polling for status updates
    startPolling() {
        this.pollingInterval = setInterval(() => {
            this.fetchStatus();
        }, 2000); // Poll every 2 seconds
        this.fetchStatus(); // Initial fetch
    }

    // Stop polling
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    // Fetch current status from backend
    async fetchStatus() {
        try {
            const response = await fetch(`/api/alert/${this.alertId}/data`);
            const data = await response.json();
            
            if (data.error) {
                console.error('Alert not found');
                this.stopPolling();
                return;
            }

            this.handleStatusUpdate(data);

            // Stop polling if workflow is complete
            if (data.status === 'RESOLVED' || data.status === 'ERROR') {
                this.stopPolling();
            }
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }

    // Handle status update and trigger UI changes
    handleStatusUpdate(data) {
        const { status, logs, route_phase, route_geometry, eta_minutes, selected_hospital, ambulance } = data;

        // Update activity log
        this.updateActivityLog(logs);

        // Update status badge
        this.updateStatusBadge(status);

        // Update map route
        if (route_geometry && route_phase) {
            this.updateMapRoute(route_geometry, route_phase);
        }

        // Update ETA display
        if (eta_minutes) {
            this.updateETA(eta_minutes);
        }

        // Update hospital info
        if (selected_hospital) {
            this.updateHospitalInfo(selected_hospital);
        }

        // Trigger custom callbacks
        this.statusCallbacks.forEach(callback => callback(data));
    }

    // Update activity log in sidebar
    updateActivityLog(logs) {
        const logContainer = document.getElementById('activity-log');
        if (!logContainer || !logs) return;

        logContainer.innerHTML = logs.map(log => 
            `<div class="log-entry">${log}</div>`
        ).join('');
        
        // Scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    // Update status badge
    updateStatusBadge(status) {
        const statusBadge = document.getElementById('alert-status');
        if (!statusBadge) return;

        const statusMap = {
            'SEARCHING_HOSPITALS': { text: 'Searching Hospitals', color: 'bg-yellow-500' },
            'HOSPITAL_SELECTED': { text: 'Hospital Selected', color: 'bg-blue-500' },
            'DISPATCHING_AMBULANCE': { text: 'Dispatching Ambulance', color: 'bg-blue-500' },
            'EN_ROUTE_TO_PATIENT': { text: 'En Route to Patient', color: 'bg-cyan-500' },
            'PATIENT_PICKUP': { text: 'Patient Pickup', color: 'bg-orange-500' },
            'EN_ROUTE_TO_HOSPITAL': { text: 'En Route to Hospital', color: 'bg-red-500' },
            'RESOLVED': { text: 'Mission Complete', color: 'bg-green-500' },
            'ERROR': { text: 'Error', color: 'bg-red-700' }
        };

        const statusInfo = statusMap[status] || { text: 'Processing', color: 'bg-gray-500' };
        statusBadge.textContent = statusInfo.text;
        statusBadge.className = `px-3 py-1 rounded-full text-white text-sm ${statusInfo.color}`;
    }

    // Update map route visualization
    updateMapRoute(geometry, phase) {
        if (!this.map || !geometry) return;

        // Remove previous route
        if (this.currentRoute) {
            this.map.removeLayer(this.currentRoute);
        }

        // Decode polyline geometry (assuming it's GeoJSON or encoded polyline)
        const coordinates = this.decodeGeometry(geometry);
        
        // Color based on phase
        const color = phase === 'TO_PATIENT' ? '#3b82f6' : '#ef4444'; // Blue or Red

        // Add new route to map
        this.currentRoute = L.polyline(coordinates, {
            color: color,
            weight: 4,
            opacity: 0.7
        }).addTo(this.map);

        // Fit map to route bounds
        this.map.fitBounds(this.currentRoute.getBounds());
    }

    // Decode geometry (simplified - adjust based on your format)
    decodeGeometry(geometry) {
        // If geometry is already an array of coordinates
        if (Array.isArray(geometry)) {
            return geometry;
        }
        
        // If it's a GeoJSON string
        try {
            const geojson = JSON.parse(geometry);
            return geojson.coordinates.map(coord => [coord[1], coord[0]]); // Swap lng/lat to lat/lng
        } catch (e) {
            console.error('Error decoding geometry:', e);
            return [];
        }
    }

    // Update ETA display
    updateETA(minutes) {
        const etaElement = document.getElementById('eta-display');
        if (etaElement) {
            etaElement.textContent = `ETA: ${minutes} mins`;
        }
    }

    // Update hospital info panel
    updateHospitalInfo(hospital) {
        const hospitalPanel = document.getElementById('hospital-info');
        if (!hospitalPanel) return;

        hospitalPanel.innerHTML = `
            <h3 class="font-bold">${hospital.name}</h3>
            <p>Distance: ${hospital.distance_km} km</p>
            <p>Service: ${hospital.service}</p>
        `;
    }

    // Register custom callback for status changes
    onStatusChange(callback) {
        this.statusCallbacks.push(callback);
    }
}

// Initialize workflow manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    const alertId = window.location.pathname.split('/').pop();
    
    // Wait for map to be initialized
    if (typeof map !== 'undefined') {
        window.workflowManager = new EmergencyWorkflowManager(alertId, map);
        window.workflowManager.startPolling();
    }
});
