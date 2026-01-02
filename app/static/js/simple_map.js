/**
 * SimpleMap - Initialisation de la carte Leaflet
 * Version Épurée pour MediAlert (Sans conflits)
 */
class SimpleMap {
    constructor(divId, lat, lng, patientName) {
        this.map = null;
        this.initMap(divId, lat, lng, patientName);
    }

    initMap(divId, lat, lng, name) {
        // 1. Création de la carte
        this.map = L.map(divId).setView([lat, lng], 14);

        // 2. Ajout des tuiles (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // 3. Marqueur Patient (Bleu fixe par défaut)
        const patientIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });

        L.marker([lat, lng], {icon: patientIcon})
            .addTo(this.map)
            .bindPopup(`<b>${name}</b><br>Position Patient`)
            .openPopup();
        
        console.log("✅ [SimpleMap] Carte initialisée avec succès.");
    }
}