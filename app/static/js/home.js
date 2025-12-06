let map;
let currentTileLayer;
let hospitalMarkers = [];

// Map tile configurations
const mapTiles = {
    dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
};

// Hospital icon
const hospitalIcon = L.divIcon({
    html: '<i class="fas fa-hospital text-2xl hospital-marker"></i>',
    iconSize: [30, 30],
    className: 'custom-div-icon'
});

// Initialize map
function initializeMap() {
    map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }).setView([33.5731, -7.5898], 6);
    
    const isDark = !document.body.classList.contains('light-mode');
    currentTileLayer = L.tileLayer(mapTiles[isDark ? 'dark' : 'light'], {
        attribution: '© OpenStreetMap'
    }).addTo(map);
    
    loadHospitals();
}

// Load hospitals from JSON
async function loadHospitals() {
    try {
        const response = await fetch('/static/data/hospitals.json');
        const hospitals = await response.json();
        
        hospitals.forEach(hospital => {
            const marker = L.marker([hospital.lat, hospital.lng], { icon: hospitalIcon })
                .addTo(map)
                .bindPopup(`
                    <div class="p-2 popup-content">
                        <h4 class="font-semibold text-cyan-400">${hospital.name}</h4>
                        <p class="text-xs text-slate-300">${hospital.locality}</p>
                    </div>
                `);
            hospitalMarkers.push(marker);
        });
        
        document.getElementById('hospitalCount').textContent = hospitals.length;
    } catch (error) {
        console.error('Error loading hospitals:', error);
        document.getElementById('hospitalCount').textContent = '0';
    }
}

// Switch map tiles
function switchMapTiles(theme) {
    if (currentTileLayer) {
        map.removeLayer(currentTileLayer);
    }
    currentTileLayer = L.tileLayer(mapTiles[theme], {
        attribution: '© OpenStreetMap'
    }).addTo(map);
}

// Theme toggle handler
function handleThemeToggle() {
    const isDark = !document.body.classList.contains('light-mode');
    switchMapTiles(isDark ? 'dark' : 'light');
}

// Timeline animation
function animateTimeline() {
    const steps = document.querySelectorAll('.timeline-step');
    const connectors = document.querySelectorAll('.timeline-connector');
    let currentStep = 0;
    
    setInterval(() => {
        steps.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            if (index < currentStep) {
                step.classList.add('completed');
            } else if (index === currentStep) {
                step.classList.add('active');
            }
        });
        
        connectors.forEach((connector, index) => {
            connector.classList.remove('active');
            if (index < currentStep) {
                connector.classList.add('active');
            }
        });
        
        currentStep = (currentStep + 1) % steps.length;
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    animateTimeline();
    
    // Listen for theme changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                handleThemeToggle();
            }
        });
    });
    
    observer.observe(document.body, { attributes: true });
});
