/**
 * Emergency Workflow Manager - Version FINALE (Cohérence Totale)
 * Inclus : Animation Fluide + Calcul Distances Uniformisé
 */

class EmergencyWorkflowManager {
    constructor(alertId, mapInstance, patientCoords) {
        this.alertId = alertId;
        this.map = mapInstance;
        this.patientCoords = patientCoords; // {lat: x, lng: y}
        this.pollingInterval = null;
        this.currentRouteLayer = null;
        this.ambulanceMarker = null;
        this.hospitalMarker = null;
        this.hasZoomed = false;
        
        // --- Variables d'animation ---
        this.animationFrame = null; 
        this.currentRouteColor = '#ef4444'; 

        this.createAmbulanceIcon = (color = '#ef4444') => {
            return L.divIcon({
                html: `<i class="fas fa-ambulance" style="color: ${color}; font-size: 24px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));"></i>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16],
                popupAnchor: [0, -16],
                className: 'ambulance-icon transition-colors duration-300'
            });
        };

        this.ambulanceIcon = this.createAmbulanceIcon();
        console.log("🚀 [Manager] Démarrage (Distances Synchronisées)...");
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        if (!lat1 || !lon1 || !lat2 || !lon2) return "--";
        const R = 6371; 
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return (R * c).toFixed(2); 
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
        const { status, route_active, route_red, route_blue, selected_hospital, ambulance } = data;

        this.updateUI(data);

        if (selected_hospital) this.drawHospital(selected_hospital);

        if (route_active === 'RED' && route_red) {
            this.drawRoute(route_red, '#ef4444');
            this.currentRouteColor = '#ef4444'; 
        } else if (route_active === 'BLUE' && route_blue) {
            this.drawRoute(route_blue, '#3b82f6');
            this.currentRouteColor = '#3b82f6';
        }

        if (ambulance) {
            this.updateAmbulanceSmooth(ambulance);
        }
    }

    updateAmbulanceSmooth(amb) {
        let lat = parseFloat(amb.current_lat), lng = parseFloat(amb.current_lng);
        if (lat < 0 && lng > 0) { let t = lat; lat = lng; lng = t; }
        if (isNaN(lat)) return;
        
        const newTargetPos = [lat, lng];
        const popupText = "<b><i class=\"fas fa-ambulance mr-1\"></i> Ambulance SMUR</b>";
        
        if (!this.ambulanceMarker) {
            this.ambulanceIcon = this.createAmbulanceIcon(this.currentRouteColor);
            this.ambulanceMarker = L.marker(newTargetPos, {
                icon: this.ambulanceIcon, 
                zIndexOffset: 1000
            }).addTo(this.map).bindPopup(popupText);
            return; 
        } 

        const newIcon = this.createAmbulanceIcon(this.currentRouteColor);
        this.ambulanceMarker.setIcon(newIcon);

        const currentMarkerLatLng = this.ambulanceMarker.getLatLng();
        const startPos = [currentMarkerLatLng.lat, currentMarkerLatLng.lng];

        this.animateMarker(startPos, newTargetPos, 1000);
    }

    animateMarker(startPos, endPos, duration) {
        if (this.animationFrame) cancelAnimationFrame(this.animationFrame);
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentLat = startPos[0] + (endPos[0] - startPos[0]) * progress;
            const currentLng = startPos[1] + (endPos[1] - startPos[1]) * progress;

            this.ambulanceMarker.setLatLng([currentLat, currentLng]);

            if (progress < 1) {
                this.animationFrame = requestAnimationFrame(animate);
            } else {
                this.ambulanceMarker.setLatLng(endPos);
                this.animationFrame = null;
            }
        };
        this.animationFrame = requestAnimationFrame(animate);
    }

    drawHospital(hospital) {
        if (this.hospitalMarker) return;
        let lat = parseFloat(hospital.coordinates?.lat || hospital.lat);
        let lng = parseFloat(hospital.coordinates?.lng || hospital.lng);
        if (isNaN(lat) || isNaN(lng)) return;
        if (lat < 0 && lng > 0) { let t = lat; lat = lng; lng = t; } 

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
        
        // --- MODIFICATION ICI : Hôpital Info avec Calcul Réel ---
        const hospInfo = document.getElementById('hospital-info');
        if(hospInfo && data.selected_hospital) {
            let distDisplay = "--";
            
            // Si on a les coordonnées du patient, on calcule la vraie distance
            if (this.patientCoords) {
                let hospLat = parseFloat(data.selected_hospital.coordinates?.lat || data.selected_hospital.lat);
                let hospLng = parseFloat(data.selected_hospital.coordinates?.lng || data.selected_hospital.lng);
                if (hospLat < 0 && hospLng > 0) { let t = hospLat; hospLat = hospLng; hospLng = t; }

                distDisplay = this.calculateDistance(
                    this.patientCoords.lat, this.patientCoords.lng,
                    hospLat, hospLng
                );
            } else {
                // Fallback (ne devrait pas arriver si le HTML est à jour)
                distDisplay = data.selected_hospital.distance_km || "--";
            }

            hospInfo.innerHTML = `<div class="text-center"><h3 class="font-bold text-cyan-500">${data.selected_hospital.name}</h3><p class="text-xs text-slate-400">${distDisplay} km</p></div>`;
        }
        
        // Info Ambulance
        const ambName = document.getElementById('amb-name-display');
        if(ambName && data.ambulance) {
            ambName.innerText = data.ambulance.id || "SMUR-01";
        }

        // --- GESTION DES DISTANCES LOGISTIQUE ---
        const distAmb = document.getElementById('dist_amb_pat');
        const distHosp = document.getElementById('dist_pat_hosp');
        
        // 1. Distance Ambulance -> Patient (Dynamique)
        if (distAmb && data.ambulance && this.patientCoords) {
            let ambLat = parseFloat(data.ambulance.current_lat);
            let ambLng = parseFloat(data.ambulance.current_lng);
            if (ambLat < 0 && ambLng > 0) { let t = ambLat; ambLat = ambLng; ambLng = t; }

            const distanceCalculee = this.calculateDistance(
                ambLat, ambLng,
                this.patientCoords.lat, this.patientCoords.lng
            );
            distAmb.innerText = (data.dist_amb_pat || distanceCalculee) + " km";
        }

        // 2. Distance Patient -> Hôpital (Phase 2 - Fixe)
        if (distHosp) {
            if (data.selected_hospital && this.patientCoords) {
                let hospLat = parseFloat(data.selected_hospital.coordinates?.lat || data.selected_hospital.lat);
                let hospLng = parseFloat(data.selected_hospital.coordinates?.lng || data.selected_hospital.lng);
                if (hospLat < 0 && hospLng > 0) { let t = hospLat; hospLat = hospLng; hospLng = t; }

                // Même calcul que pour hospInfo ci-dessus
                const distFixe = this.calculateDistance(
                    this.patientCoords.lat, this.patientCoords.lng,
                    hospLat, hospLng
                );
                distHosp.innerText = distFixe + " km";
            } else {
                distHosp.innerText = "-- km";
            }
        }

        // Triage
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
}

document.addEventListener('DOMContentLoaded', () => {
    const alertId = window.location.pathname.split('/').pop();
    
    // Récupération des coords depuis le template HTML
    const patientPos = (window.patientLat && window.patientLng) 
        ? { lat: window.patientLat, lng: window.patientLng } 
        : null;

    const t = setInterval(() => {
        if (window.map) {
            clearInterval(t);
            console.log("✅ Map Prête. Init Manager avec PatientPos:", patientPos);
            window.workflowManager = new EmergencyWorkflowManager(alertId, window.map, patientPos);
            window.workflowManager.startPolling();
        }
    }, 200);
});