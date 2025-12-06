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
        allHospitals = hospitals; // Store for search
        
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
        if (document.getElementById('totalHospitals')) {
            document.getElementById('totalHospitals').textContent = hospitals.length;
        }
        
        // Display random 5 hospitals in the list
        if (document.getElementById('hospitalList')) {
            const randomHospitals = hospitals.sort(() => 0.5 - Math.random()).slice(0, 5);
            const listHTML = randomHospitals.map(h => `
                <div class="border-l-4 border-cyan-500 pl-4 py-2">
                    <h4 class="font-semibold text-white">${h.name}</h4>
                    <p class="text-sm text-slate-400">
                        <i class="fas fa-map-marker-alt text-cyan-400"></i> ${h.locality}
                    </p>
                </div>
            `).join('');
            document.getElementById('hospitalList').innerHTML = listHTML;
        }
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

// Search functionality
let allHospitals = [];

function setupSearch() {
    const searchInput = document.getElementById('mapSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        
        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }
        
        const filtered = allHospitals.filter(h => 
            h.name.toLowerCase().includes(query) || 
            h.locality.toLowerCase().includes(query)
        ).slice(0, 5);
        
        if (filtered.length > 0) {
            searchResults.innerHTML = filtered.map(h => `
                <div class="p-3 hover:bg-cyan-500/10 cursor-pointer rounded border-b border-cyan-500/10" 
                     onclick="zoomToHospital(${h.lat}, ${h.lng}, '${h.name.replace(/'/g, "\\'")}')">>
                    <div class="font-semibold text-white">${h.name}</div>
                    <div class="text-xs text-slate-400">
                        <i class="fas fa-map-marker-alt text-cyan-400"></i> ${h.locality}
                    </div>
                </div>
            `).join('');
            searchResults.classList.remove('hidden');
        } else {
            searchResults.innerHTML = '<div class="p-3 text-slate-400 text-sm">Aucun résultat trouvé</div>';
            searchResults.classList.remove('hidden');
        }
    });
    
    // Close results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });
}

window.zoomToHospital = function(lat, lng, name) {
    map.setView([lat, lng], 15);
    document.getElementById('searchResults').classList.add('hidden');
    document.getElementById('mapSearch').value = name;
    
    // Find and open popup
    hospitalMarkers.forEach(marker => {
        if (marker.getLatLng().lat === lat && marker.getLatLng().lng === lng) {
            marker.openPopup();
        }
    });
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    animateTimeline();
    setupSearch();
    
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
