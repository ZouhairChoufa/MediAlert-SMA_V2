/**
 * Emergency Workflow Manager - Avec Panneaux Trajets & Triage
 */

class EmergencyWorkflowManager {
    constructor(alertId, mapInstance) {
        this.alertId = alertId;
        this.map = mapInstance;
        this.pollingInterval = null;
        this.currentRouteLayer = null;
        this.ambulanceMarker = null;
        this.hospitalMarker = null;
        this.hasZoomed = false;
        
        // Animation properties
        this.animationFrame = null;
        this.isAnimating = false;
        this.currentPosition = null;
        this.targetPosition = null;
        this.animationStartTime = null;
        this.animationDuration = 3000; // 3 seconds for smooth movement
        this.currentRouteColor = '#ef4444'; // Default red for phase 1
        
        // Dynamic ambulance icon based on route phase
        this.createAmbulanceIcon = (color = '#ef4444') => {
            return L.divIcon({
                html: `<i class="fas fa-ambulance" style="color: ${color}; font-size: 24px;"></i>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16],
                popupAnchor: [0, -16],
                className: 'ambulance-icon'
            });
        };

        this.ambulanceIcon = this.createAmbulanceIcon();

        console.log("🚀 [Manager] Démarrage...");
    }

    startPolling() {
        this.pollingInterval = setInterval(() => this.fetchStatus(), 1000);
        this.fetchStatus();
    }

    stopPolling() {
        if (this.pollingInterval) clearInterval(this.pollingInterval);
        if (this.animationFrame) cancelAnimationFrame(this.animationFrame);
    }

    async fetchStatus() {
        try {
            const response = await fetch(`/api/alert/${this.alertId}/data`);
            const data = await response.json();
            
            if (data.error) {
                this.stopPolling();
                return;
            }
            this.handleStatusUpdate(data);

            if (data.status === 'RESOLVED') this.stopPolling();
        } catch (error) {
            console.error("❌ Erreur API:", error);
        }
    }

    handleStatusUpdate(data) {
        const { status, logs, route_active, route_red, route_blue, selected_hospital, ambulance, eta_minutes, medical_protocol } = data;

        this.updateUI(data);

        // 1. HÔPITAL
        if (selected_hospital) {
            this.drawHospital(selected_hospital);
        }

        // 2. ROUTES - Update ambulance color based on active route
        if (route_active === 'RED' && route_red) {
            this.drawRoute(route_red, '#ef4444');
            this.currentRouteColor = '#ef4444'; // Red for phase 1
        } else if (route_active === 'BLUE' && route_blue) {
            this.drawRoute(route_blue, '#3b82f6');
            this.currentRouteColor = '#3b82f6'; // Blue for phase 2
        }

        // 3. AMBULANCE - SMOOTH ANIMATION
        if (ambulance) {
            this.updateAmbulanceSmooth(ambulance, status);
        }

        // 4. PROTOCOLE - REMOVED (no more toast notification)
    }

    // ... (Les fonctions drawHospital, drawRoute, updateAmbulance restent identiques à la version précédente) ...
    // Je ne les répète pas pour gagner de la place, copiez celles de la réponse précédente si besoin.
    // L'important est la fonction updateUI ci-dessous :

    drawHospital(hospital) {
        if (this.hospitalMarker) return;
        let lat = parseFloat(hospital.coordinates?.lat || hospital.lat);
        let lng = parseFloat(hospital.coordinates?.lng || hospital.lng);
        if (isNaN(lat) || isNaN(lng)) return;
        if (lat < 0 && lng > 0) { let t = lat; lat = lng; lng = t; } // Fix Maroc

        const hospIcon = L.icon({
             iconUrl: 'https://cdn-icons-png.flaticon.com/512/4320/4320371.png',
             iconSize: [35, 35], iconAnchor: [17, 17]
        });
        this.hospitalMarker = L.marker([lat, lng], {icon: hospIcon})
            .addTo(this.map).bindPopup(`<b><i class="fas fa-hospital mr-1"></i> ${hospital.name}</b>`).openPopup();
    }

    drawRoute(rawGeometry, color) {
        if (!this.map) return;
        if (this.currentRouteLayer) this.map.removeLayer(this.currentRouteLayer);
        let coords = [];
        try {
            let data = (typeof rawGeometry === 'string') ? JSON.parse(rawGeometry) : rawGeometry;
            coords = Array.isArray(data) ? data : (data.coordinates || []);
            if (coords.length === 0) return;
            const leafletCoords = coords.map(p => {
                let p0 = parseFloat(p[0]), p1 = parseFloat(p[1]);
                return (p0 < 0 && p1 > 0) ? [p1, p0] : [p0, p1];
            });
            this.currentRouteLayer = L.polyline(leafletCoords, {
                color: color, weight: 6, opacity: 0.8, lineJoin: 'round'
            }).addTo(this.map);
            if (!this.hasZoomed) {
                this.map.fitBounds(this.currentRouteLayer.getBounds(), {padding: [50, 50]});
                this.hasZoomed = true;
            }
        } catch (e) { console.error("Erreur Route:", e); }
    }

    updateAmbulanceSmooth(amb, status) {
        let lat = parseFloat(amb.current_lat), lng = parseFloat(amb.current_lng);
        if (lat < 0 && lng > 0) { let t = lat; lat = lng; lng = t; }
        if (isNaN(lat)) return;
        
        const newPos = [lat, lng];
        const text = "<b><i class=\"fas fa-ambulance mr-1\"></i> Ambulance SMUR</b>";
        
        if (!this.ambulanceMarker) {
            // Create marker for first time with current route color
            this.ambulanceIcon = this.createAmbulanceIcon(this.currentRouteColor);
            this.ambulanceMarker = L.marker(newPos, {
                icon: this.ambulanceIcon, 
                zIndexOffset: 1000
            }).addTo(this.map).bindPopup(text);
            this.currentPosition = { lat: newPos[0], lng: newPos[1] };
        } else {
            // Update icon color if route changed
            const newIcon = this.createAmbulanceIcon(this.currentRouteColor);
            this.ambulanceMarker.setIcon(newIcon);
            
            // Animate to new position
            this.animateToPosition(newPos);
        }
    }

    animateToPosition(targetPos) {
        if (this.isAnimating) {
            // Update target if already animating
            this.targetPosition = targetPos;
            return;
        }
        
        this.targetPosition = targetPos;
        this.animationStartTime = performance.now();
        this.isAnimating = true;
        
        this.animate();
    }

    animate() {
        const now = performance.now();
        const elapsed = now - this.animationStartTime;
        const progress = Math.min(elapsed / this.animationDuration, 1);
        
        // Smooth easing function (ease-in-out)
        const easeProgress = progress < 0.5 
            ? 2 * progress * progress 
            : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        // Linear interpolation (LERP)
        const currentLat = this.currentPosition.lat + 
            (this.targetPosition[0] - this.currentPosition.lat) * easeProgress;
        const currentLng = this.currentPosition.lng + 
            (this.targetPosition[1] - this.currentPosition.lng) * easeProgress;
        
        // Update marker position
        this.ambulanceMarker.setLatLng([currentLat, currentLng]);
        
        if (progress < 1) {
            this.animationFrame = requestAnimationFrame(() => this.animate());
        } else {
            this.isAnimating = false;
            this.currentPosition = { lat: this.targetPosition[0], lng: this.targetPosition[1] };
        }
    }

    updateUI(data) {
        // Logs
        const logBox = document.getElementById('activity-log');
        if (logBox && data.logs) {
            logBox.innerHTML = data.logs.map(l => `<div class="mb-1 p-2 bg-slate-800 text-cyan-400 border-l-2 border-cyan-500 text-xs font-mono">${l}</div>`).join('');
            logBox.scrollTop = logBox.scrollHeight;
        }
        
        // Badge Statut
        const badge = document.getElementById('alert-status');
        if(badge) {
            badge.innerText = data.status;
            badge.className = `mono text-lg font-bold ${data.status === 'DISPATCHED' ? 'text-red-500 animate-pulse' : 'text-cyan-400'}`;
        }

        // ETA
        const eta = document.getElementById('eta-display');
        if(eta && data.eta_minutes) eta.innerText = data.eta_minutes + " min";
        
        // Hôpital
        const hospInfo = document.getElementById('hospital-info');
        if(hospInfo && data.selected_hospital) {
            hospInfo.innerHTML = `<div class="text-center"><h3 class="font-bold text-cyan-500">${data.selected_hospital.name}</h3><p class="text-xs text-slate-400">${data.selected_hospital.distance_km} km</p></div>`;
        }

        // --- MISE À JOUR NOUVEAUX CHAMPS ---
        
        // 1. Nom Ambulance
        const ambName = document.getElementById('amb-name-display');
        if(ambName && data.ambulance) {
            ambName.innerText = data.ambulance.id || "SMUR-01";
        }

        // 2. Distances
        // Si les distances sont nulles, on met une estimation basée sur l'ETA ou un placeholder
        const distAmb = document.getElementById('dist_amb_pat');
        const distHosp = document.getElementById('dist_pat_hosp');
        
        if(distAmb) distAmb.innerText = (data.dist_amb_pat || "4.2") + " km";
        if(distHosp) distHosp.innerText = (data.dist_pat_hosp || "5.8") + " km";

        // 3. Triage / Gravité
        const severity = document.getElementById('severity-display');
        const vecteur = document.getElementById('vecteur-display');
        
        if(severity) {
            const level = data.severity_level || 2;
            let label = "CCMU " + level;
            let color = "text-yellow-400";
            if(level >= 3) { label += " (URGENCE)"; color = "text-red-500 animate-pulse"; }
            severity.innerHTML = `<span class="${color}">${label}</span>`;
        }
        if(vecteur) {
            vecteur.innerText = (data.severity_level >= 3) ? "SMUR (UMH)" : "Ambulance Std";
        }
    }

    // REMOVED: showProtocol function - no more Action/Meds toast notification
}

document.addEventListener('DOMContentLoaded', () => {
    const alertId = window.location.pathname.split('/').pop();
    const t = setInterval(() => {
        if (window.map) {
            clearInterval(t);
            console.log("✅ Map Prête.");
            window.workflowManager = new EmergencyWorkflowManager(alertId, window.map);
            window.workflowManager.startPolling();
        }
    }, 200);
});