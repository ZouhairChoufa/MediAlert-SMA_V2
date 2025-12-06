let map;
let ambulanceMarker;
let routePolyline;
let hospitalMarkers = [];
let animationFrame;
let currentRoute = null;
let animationProgress = 0;
let currentSpeed = 0;

// Custom ambulance icon
const ambulanceIcon = L.divIcon({
    html: '<i class="fas fa-ambulance text-red-500 text-2xl"></i>',
    iconSize: [30, 30],
    className: 'custom-div-icon'
});

// Custom hospital icon
const hospitalIcon = L.divIcon({
    html: '<i class="fas fa-hospital text-blue-500 text-xl"></i>',
    iconSize: [25, 25],
    className: 'custom-div-icon'
});

let currentTileLayer;

function initializeMap() {
    map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }).setView([33.5731, -7.5898], 11);
    
    // Set tiles based on current theme
    const isDark = !document.body.classList.contains('light-mode');
    const tileUrl = isDark 
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
    
    currentTileLayer = L.tileLayer(tileUrl, {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Listen for theme changes
    const observer = new MutationObserver(() => {
        const isDark = !document.body.classList.contains('light-mode');
        const newTileUrl = isDark
            ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
            : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
        
        if (currentTileLayer) {
            map.removeLayer(currentTileLayer);
        }
        currentTileLayer = L.tileLayer(newTileUrl, {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    });
    
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    
    loadHospitals();
}

async function loadHospitals() {
    try {
        const response = await fetch('/static/data/hospitals.json');
        const hospitals = await response.json();
        
        hospitals.forEach(hospital => {
            const marker = L.marker([hospital.lat, hospital.lng], { icon: hospitalIcon })
                .addTo(map)
                .bindPopup(`
                    <div class="p-2">
                        <h4 class="font-semibold text-cyan-400">${hospital.name}</h4>
                        <p class="text-xs text-slate-300">${hospital.locality}</p>
                    </div>
                `);
            hospitalMarkers.push(marker);
        });
    } catch (error) {
        console.error('Error loading hospitals:', error);
    }
}

function startAmbulanceTracking(routeData) {
    if (!routeData || !routeData.coordinates) return;
    
    currentRoute = routeData.coordinates;
    animationProgress = 0;
    
    // Clear existing route and ambulance
    if (routePolyline) {
        map.removeLayer(routePolyline);
    }
    if (ambulanceMarker) {
        map.removeLayer(ambulanceMarker);
    }
    
    // Draw route polyline
    routePolyline = L.polyline(currentRoute, {
        color: '#ef4444',
        weight: 4,
        opacity: 0.8
    }).addTo(map);
    
    // Fit map to route
    map.fitBounds(routePolyline.getBounds(), { padding: [20, 20] });
    
    // Start ambulance at first coordinate
    ambulanceMarker = L.marker(currentRoute[0], { icon: ambulanceIcon }).addTo(map);
    
    // Start animation
    animateAmbulance();
}

function animateAmbulance() {
    if (!currentRoute || animationProgress >= 1) return;
    
    // Calculate current position along route
    const totalPoints = currentRoute.length - 1;
    const currentIndex = Math.floor(animationProgress * totalPoints);
    const nextIndex = Math.min(currentIndex + 1, totalPoints);
    
    if (currentIndex < totalPoints) {
        const current = currentRoute[currentIndex];
        const next = currentRoute[nextIndex];
        
        // Interpolate between current and next point
        const segmentProgress = (animationProgress * totalPoints) - currentIndex;
        const lat = current[0] + (next[0] - current[0]) * segmentProgress;
        const lng = current[1] + (next[1] - current[1]) * segmentProgress;
        
        // Update ambulance position with smooth transition
        ambulanceMarker.setLatLng([lat, lng]);
        
        // Calculate speed (simulated)
        currentSpeed = 60 + Math.random() * 20;
        document.getElementById('speed').textContent = Math.round(currentSpeed) + ' km/h';
        
        // Update progress
        animationProgress += 0.002;
        
        // Continue animation
        animationFrame = requestAnimationFrame(animateAmbulance);
    }
}

function stopAmbulanceTracking() {
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
    }
    animationProgress = 0;
    currentRoute = null;
}

function updateAmbulanceRoute(newRouteData) {
    stopAmbulanceTracking();
    startAmbulanceTracking(newRouteData);
}

function highlightDestinationHospital(hospitalName) {
    hospitalMarkers.forEach(marker => {
        const popup = marker.getPopup();
        if (popup && popup.getContent().includes(hospitalName)) {
            marker.openPopup();
            // Add pulsing effect
            marker.getElement().style.animation = 'pulse 2s infinite';
        }
    });
}

// ETA countdown functionality
let etaCountdown;
let etaEndTime;

function startETACountdown(etaMinutes) {
    etaEndTime = new Date(Date.now() + etaMinutes * 60000);
    
    etaCountdown = setInterval(() => {
        const now = new Date();
        const timeLeft = etaEndTime - now;
        
        if (timeLeft <= 0) {
            clearInterval(etaCountdown);
            document.getElementById('etaCounter').textContent = '00:00';
            showArrivalNotification();
            return;
        }
        
        const minutes = Math.floor(timeLeft / 60000);
        const seconds = Math.floor((timeLeft % 60000) / 1000);
        
        document.getElementById('etaCounter').textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopETACountdown() {
    if (etaCountdown) {
        clearInterval(etaCountdown);
    }
}

function showArrivalNotification() {
    // Show toast notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white p-4 rounded-lg shadow-lg z-50';
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas fa-check-circle"></i>
            <span>Ambulance arrivée à destination</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Export functions for use in dashboard
window.mapFunctions = {
    startAmbulanceTracking,
    stopAmbulanceTracking,
    updateAmbulanceRoute,
    highlightDestinationHospital,
    startETACountdown,
    stopETACountdown
};