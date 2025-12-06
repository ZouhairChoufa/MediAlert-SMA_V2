# 🚑 MediAlert SMA - Système Multi-Agents d'Urgence Médicale

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-purple.svg)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange.svg)](https://groq.com/)

> **AI-powered emergency medical dispatch system** coordinating ambulances, hospitals, and medical teams through intelligent multi-agent collaboration.

[🇫🇷 Version Française](README.md) | [📖 Setup Guide](SETUP.md) | [🤝 Contributing](CONTRIBUTING.md)

---

## ✨ Key Features

### 🤖 Multi-Agent AI System
- **7 Specialized Agents** working in harmony for emergency management
- **Intelligent Triage** with automatic symptom analysis
- **Smart Routing** with optimal ambulance dispatch
- **Real-time Coordination** between all emergency services

### 🗺️ Real-Time Geospatial Tracking
- **Interactive Maps** with live visualization
- **GPS Location Detection** with IP fallback
- **Route Animation** at 60 FPS on real roads
- **ETA Countdown** with live updates

### 🌍 Smart Geolocation
- **Automatic IP Detection** using AbstractAPI
- **GPS Integration** with browser geolocation
- **Manual Input Validation** with intelligent fallback
- **Multi-source Merging** (GPS > Manual > IP)

### 🎨 Modern UI/UX
- **Dark/Light Mode** with seamless transitions
- **Engineering-Style Design** with glassmorphism
- **Responsive Layout** for all devices
- **Real-time Updates** without page refresh

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip package manager
- API Keys (all FREE):
  - [Groq API](https://console.groq.com) - AI models
  - [OpenRouteService](https://openrouteservice.org/dev/#/signup) - Routing
  - [AbstractAPI](https://www.abstractapi.com/api/ip-geolocation-api) - IP Geolocation

### Installation (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-username/medialert-sma.git
cd medialert-sma

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
copy config\.env.example config\.env
# Edit config/.env with your API keys

# 6. Run application
python run.py
```

### Access Application
- **Home**: http://localhost:5000
- **Dashboard**: http://localhost:5000/dashboard
- **Create Alert**: http://localhost:5000/alert

---

## 📸 Screenshots

### Landing Page
Modern command center interface with hospital monitoring and emergency response timeline.

### Emergency Alert Form
GPS-powered location detection with automatic IP fallback for precise patient positioning.

### Live Tracking
Real-time ambulance animation on actual roads with ETA countdown and route visualization.

### Dark/Light Mode
Seamless theme switching with synchronized map tiles and UI elements.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              MediAlert SMA - Architecture                │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Frontend (Flask Templates + Tailwind CSS)              │
│  ├── Landing Page (index.html)                          │
│  ├── Dashboard (dashboard.html)                         │
│  ├── Alert Form (alert_form.html)                       │
│  └── Live Tracking (tracking.html)                      │
│                                                           │
│  Backend (Flask + Python)                                │
│  ├── Routes (API Endpoints)                             │
│  ├── Services (Business Logic)                          │
│  │   ├── GeolocationService (IP + GPS)                 │
│  │   ├── SmartDispatchEngine (Hospital Selection)      │
│  │   ├── HospitalService (Haversine + ORS)             │
│  │   └── ORSService (Route Calculation)                │
│  └── Crew (AI Agents)                                   │
│      └── 7 Specialized Agents (LangChain + Groq)       │
│                                                           │
│  External APIs                                           │
│  ├── Groq (LLM - llama-3.3-70b)                        │
│  ├── OpenRouteService (Routing)                         │
│  ├── AbstractAPI (IP Geolocation)                       │
│  └── Nominatim (Reverse Geocoding)                      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 The 7 AI Agents

1. **Agent Patient** - Alert creation and data structuring
2. **Agent Médecin Urgence** - Medical triage and severity scoring
3. **Agent Coordonnateur** - Resource orchestration and hospital selection
4. **Agent Ambulance** - Route calculation and ETA estimation
5. **Agent Hôpital** - Bed availability and team preparation
6. **Agent Médecin Spécialiste** - Treatment protocols
7. **Agent Administratif** - Data consolidation and reporting

---

## 🔌 API Endpoints

### Create Emergency Alert
```http
POST /api/alert
Content-Type: application/json

{
  "nom_prenom": "John Doe",
  "age": 45,
  "sexe": "M",
  "symptomes": "Chest pain",
  "localisation": "Casablanca, Morocco",
  "gps_coords": {
    "lat": 33.5731,
    "lng": -7.5898,
    "accuracy": 50
  }
}
```

### Detect IP Location
```http
POST /api/detect-ip-location
```

### Get Alert Data
```http
GET /api/alert/<alert_id>/data
```

---

## 📁 Project Structure

```
medialert_pro/
├── app/
│   ├── crew/                    # AI agents configuration
│   │   ├── config/
│   │   │   ├── agents.yaml     # Agent definitions
│   │   │   └── tasks.yaml      # Task definitions
│   │   └── crew_simple.py      # Agent orchestration
│   ├── routes/
│   │   ├── api.py              # API endpoints
│   │   └── web.py              # Web routes
│   ├── services/
│   │   ├── geolocation.py      # IP + GPS location
│   │   ├── smart_dispatch.py   # Hospital selection
│   │   ├── hospital_service.py # Haversine + ORS
│   │   ├── ors_service.py      # Route calculation
│   │   └── location_service.py # Location utilities
│   ├── static/
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript
│   │   └── data/               # Hospital JSON
│   └── templates/              # HTML pages
├── config/
│   ├── .env.example            # Environment template
│   └── .env                    # Your API keys (gitignored)
├── data/
│   └── morocco_hospitals.csv   # Hospital database
├── scripts/
│   └── requirements_fixed.txt  # Python dependencies
├── .gitignore                  # Git exclusions
├── LICENSE                     # MIT License
├── README.md                   # This file
├── SETUP.md                    # Setup guide
├── CONTRIBUTING.md             # Contribution guide
└── run.py                      # Application entry point
```

---

## 🛠️ Technologies

### Backend
- **Flask 3.0** - Web framework
- **LangChain 0.2** - AI agent orchestration
- **Groq** - LLM inference (llama-3.3-70b)
- **Pandas** - Data processing
- **Geopy** - Geospatial calculations

### Frontend
- **Tailwind CSS** - Utility-first styling
- **Leaflet.js** - Interactive maps
- **Font Awesome 6** - Icons
- **Vanilla JavaScript** - No framework overhead

### APIs
- **OpenRouteService** - Route calculation
- **AbstractAPI** - IP geolocation
- **Nominatim** - Reverse geocoding

---

## 🎯 Use Cases

### Emergency Medical Services
- Rapid alert creation with GPS detection
- Intelligent ambulance dispatch
- Real-time tracking and coordination

### Hospital Networks
- Bed availability management
- Specialist team coordination
- Patient flow optimization

### Medical Research
- Emergency response analytics
- Triage pattern analysis
- Resource utilization studies

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation
- 🌍 Translations
- 🧪 Tests

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** for lightning-fast LLM inference
- **OpenRouteService** for reliable routing
- **AbstractAPI** for IP geolocation
- **LangChain** for agent orchestration framework

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/medialert-sma/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/medialert-sma/discussions)
- **Documentation**: [Setup Guide](SETUP.md)

---

<div align="center">

**Made with ❤️ for Emergency Medical Services**

⭐ Star this repo if you find it useful!

</div>
