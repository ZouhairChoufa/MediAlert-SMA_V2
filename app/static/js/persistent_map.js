// Persistent Map Component - Theme-independent styling
class PersistentMap {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.map = null;
        this.markers = {};
        this.routes = {};
        
        // Fixed colors - never change regardless of theme
        this.colors = {
            routeToPatient: '#3b82f6',    // Blue
            routeToHospital: '#ef4444',   // Red
            hospital: '#06b6d4',          // Cyan
            ambulance: '#f59e0b',         // Amber
            patient: '#ef4444'            // Red
        };
        
        this.init(options);
    }
    
    init(options) {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Map container #${this.containerId} not found`);
            return;
        }
        
        // Force fixed background color to prevent white flashes
        container.style.backgroundColor = '#1a1a2e';
        container.style.filter = 'none';
        container.style.mixBlendMode = 'normal';
        
        // Initialize Leaflet map with dark tile layer
        this.map = L.map(this.containerId, {
            center: options.center || [33.5731, -7.5898],
            zoom: options.zoom || 13,
            zoomControl: true,
            attributionControl: false
        });
        
        // Use CartoDB Dark Matter - persistent dark style
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd'
        }).addTo(this.map);
        
        // Prevent any CSS filters from affecting the map
        const mapContainer = this.map.getContainer();
        mapContainer.style.filter = 'none !important';
        mapContainer.style.mixBlendMode = 'normal !important';
        
        return this;
    }
    
    // Add hospital marker with fixed cyan color
    addHospitalMarker(lat, lng, name) {
        const icon = L.divIcon({
            html: `<div style="background: ${this.colors.hospital}; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid #0e7490; box-shadow: 0 0 20px ${this.colors.hospital};">
                <i class="fas fa-hospital" style="color: #fff; font-size: 14px;"></i>
            </div>`,
            className: 'custom-marker',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });
        
        const marker = L.marker([lat, lng], { icon }).addTo(this.map);
        
        if (name) {
            marker.bindPopup(`<div style="color: #fff; background: #1e293b; padding: 8px; border-radius: 4px; border: 1px solid ${this.colors.hospital};">
                <strong>${name}</strong>
            </div>`);
        }
        
        this.markers.hospital = marker;
        return marker;
    }
    
    // Add ambulance marker with fixed amber color
    addAmbulanceMarker(lat, lng, id) {
        const icon = L.divIcon({
            html: `<div style="background: ${this.colors.ambulance}; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid #d97706; box-shadow: 0 0 20px ${this.colors.ambulance}; animation: pulse 2s infinite;">
                <i class="fas fa-ambulance" style="color: #fff; font-size: 16px;"></i>
            </div>`,
            className: 'custom-marker',
            iconSize: [36, 36],
            iconAnchor: [18, 18]
        });
        
        const marker = L.marker([lat, lng], { icon }).addTo(this.map);
        
        if (id) {
            marker.bindPopup(`<div style="color: #fff; background: #1e293b; padding: 8px; border-radius: 4px; border: 1px solid ${this.colors.ambulance};">
                <strong>Ambulance ${id}</strong>
            </div>`);
        }
        
        this.markers.ambulance = marker;
        return marker;
    }
    
    // Add patient marker with fixed red color
    addPatientMarker(lat, lng, name) {
        const icon = L.divIcon({
            html: `<div style="background: ${this.colors.patient}; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid #dc2626; box-shadow: 0 0 20px ${this.colors.patient};">
                <i class="fas fa-user-injured" style="color: #fff; font-size: 14px;"></i>
            </div>`,
            className: 'custom-marker',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });
        
        const marker = L.marker([lat, lng], { icon }).addTo(this.map);
        
        if (name) {
            marker.bindPopup(`<div style="color: #fff; background: #1e293b; padding: 8px; border-radius: 4px; border: 1px solid ${this.colors.patient};">
                <strong>${name}</strong>
            </div>`);
        }
        
        this.markers.patient = marker;
        return marker;
    }
    
    // Draw route with fixed color
    drawRoute(coordinates, phase = 'TO_PATIENT') {
        // Remove existing route for this phase
        if (this.routes[phase]) {
            this.map.removeLayer(this.routes[phase]);
        }
        
        // Select color based on phase
        const color = phase === 'TO_PATIENT' ? this.colors.routeToPatient : this.colors.routeToHospital;
        
        // Create polyline with fixed styling
        const route = L.polyline(coordinates, {
            color: color,
            weight: 5,
            opacity: 0.8,
            lineJoin: 'round',
            lineCap: 'round',
            dashArray: phase === 'TO_PATIENT' ? '10, 10' : null
        }).addTo(this.map);
        
        this.routes[phase] = route;
        
        // Fit map to route bounds
        this.map.fitBounds(route.getBounds(), { padding: [50, 50] });
        
        return route;
    }
    
    // Clear all routes
    clearRoutes() {
        Object.values(this.routes).forEach(route => {
            this.map.removeLayer(route);
        });
        this.routes = {};
    }
    
    // Clear specific marker
    clearMarker(type) {
        if (this.markers[type]) {
            this.map.removeLayer(this.markers[type]);
            delete this.markers[type];
        }
    }
    
    // Update ambulance position (for animation)
    updateAmbulancePosition(lat, lng) {
        if (this.markers.ambulance) {
            this.markers.ambulance.setLatLng([lat, lng]);
        }
    }
    
    // Center map on coordinates
    centerOn(lat, lng, zoom = 13) {
        this.map.setView([lat, lng], zoom);
    }
}

// Add pulse animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    /* Force map container to ignore theme filters */
    #map, .leaflet-container {
        filter: none !important;
        mix-blend-mode: normal !important;
        background-color: #1a1a2e !important;
    }
    
    /* Ensure map tiles don't invert */
    .leaflet-tile-pane {
        filter: none !important;
    }
    
    /* Custom marker styling */
    .custom-marker {
        background: transparent !important;
        border: none !important;
    }
    
    /* Popup styling */
    .leaflet-popup-content-wrapper {
        background: #1e293b !important;
        color: #fff !important;
        border: 1px solid #06b6d4 !important;
    }
    
    .leaflet-popup-tip {
        background: #1e293b !important;
    }
`;
document.head.appendChild(style);

// Export for global use
window.PersistentMap = PersistentMap;
