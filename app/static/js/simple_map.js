// Simple Static Map - No animations, theme-locked
class SimpleMap {
    constructor(containerId, patientLat, patientLng, patientName) {
        this.map = L.map(containerId, {
            center: [patientLat, patientLng],
            zoom: 14,
            zoomControl: true
        });
        
        // Standard OSM tiles - never changes
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(this.map);
        
        // Red patient marker
        const redIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        L.marker([patientLat, patientLng], { icon: redIcon })
            .addTo(this.map)
            .bindPopup(`<b>${patientName}</b><br>Patient Location`)
            .openPopup();
    }
    
    addHospitalMarker(lat, lng, name) {
        const blueIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        L.marker([lat, lng], { icon: blueIcon })
            .addTo(this.map)
            .bindPopup(`<b>${name}</b><br>Hospital`);
    }
    
    drawRoute(coordinates, color = '#3388ff') {
        L.polyline(coordinates, {
            color: color,
            weight: 4,
            opacity: 0.7
        }).addTo(this.map);
    }
}

window.SimpleMap = SimpleMap;
