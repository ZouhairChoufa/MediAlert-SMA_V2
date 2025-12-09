# MediAlert SMA v2.0 

**Enterprise-Grade Emergency Response System**

A production-ready, AI-powered emergency dispatch system combining multi-agent intelligence, real-time logistics, and professional medical interfaces.

##  Architecture Overview

MediAlert SMA orchestrates **7 specialized AI agents** using CrewAI to handle the complete emergency response workflow:

1. **Patient Agent** - Structured data capture
2. **Medical Triage Agent** - Severity assessment & resource recommendation  
3. **Coordinator Agent** - Hospital selection & resource allocation
4. **Ambulance Agent** - Route optimization & ETA calculation
5. **Hospital Agent** - Bed reservation & team preparation
6. **Specialist Agent** - Clinical protocols & checklists
7. **Administrative Agent** - Patient communication & reporting

##  Key Features

### Multi-Agent AI Decision Making
- **Medical Triage**: Automated severity scoring (CCMU/ESI)
- **Smart Dispatch**: Optimal ambulance-hospital matching
- **Real-time Coordination**: Live status updates across all agents

### Live Ambulance Tracking
- **Real Roads**: OpenRouteService integration with traffic data
- **Smooth Animation**: 60fps ambulance movement along polylines
- **ETA Countdown**: Live arrival time updates

### MediBot Assistant
- **Groq-Powered**: Advanced conversational AI
- **Emergency Detection**: Auto-redirect on critical symptoms
- **Medical Guardrails**: Safe, professional responses

### Professional Dashboard
- **Real-time Map**: Live ambulance tracking with hospital markers
- **Status Panels**: Current alerts, ETA counters, hospital info
- **Recent Alerts**: Historical data with severity indicators

##  Technical Stack

- **Backend**: Python 3.10+, Flask (App Factory Pattern)
- **AI Engine**: CrewAI + Groq API (llama-3.3-70b)
- **Database**: Firebase Firestore (Real-time sync)
- **Geospatial**: OpenRouteService (Routing) + AbstractAPI (IP Geolocation)
- **Frontend**: HTML5, TailwindCSS, Leaflet.js, Vanilla JavaScript
- **Data**: Local Morocco hospitals CSV (10 major facilities)

## 📁 Project Structure

```
medialert_sma/
├── app/
│   ├── config.py                 # Environment configuration
│   ├── services/                 # Core business logic
│   │   ├── firebase_service.py   # Real-time data persistence
│   │   ├── ors_service.py        # Route calculation & polylines
│   │   ├── location_service.py   # IP-based geolocation
│   │   └── hospital_service.py   # CSV loading & spatial search
│   ├── crew/                     # AI Agent orchestration
│   │   ├── config/
│   │   │   ├── agents.yaml       # 7-agent definitions
│   │   │   └── tasks.yaml        # Sequential workflow tasks
│   │   ├── crew.py              # MediAlertCrew class
│   │   └── tools.py             # Custom CrewAI tools
│   ├── routes/                   # Flask endpoints
│   │   ├── web.py               # Dashboard & forms
│   │   ├── api.py               # REST API endpoints
│   │   └── chat.py              # MediBot conversations
│   ├── static/
│   │   ├── js/
│   │   │   ├── dashboard.js     # Real-time UI updates
│   │   │   └── map_animation.js # Ambulance tracking logic
│   │   └── css/                 # Custom styles
│   └── templates/
│       ├── base.html            # Professional layout
│       ├── dashboard.html       # Main control center
│       └── components/          # Reusable UI components
├── morocco_hospitals.csv        # Hospital database
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
└── run.py                      # Application entry point
```

##  Installation & Setup

### 1. Environment Setup
```bash
# Clone and navigate
cd medialert_sma

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure API Keys
Edit `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
ORS_API_KEY=your_openrouteservice_api_key_here
ABSTRACT_API_KEY=your_abstract_api_key_here
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
```

### 3. Firebase Setup
1. Create Firebase project
2. Enable Firestore Database
3. Download service account credentials JSON
4. Update `FIREBASE_CREDENTIALS_PATH` in `.env`

### 4. Run Application
```bash
python run.py
```

Access dashboard at: `http://localhost:5000`

##  API Endpoints

### Core Emergency API
- `POST /api/alert` - Create new emergency alert
- `GET /api/status/<alert_id>` - Get real-time alert status
- `GET /api/alerts/active` - Current active alerts
- `GET /api/alerts/recent` - Recent alerts for dashboard

### MediBot Chat
- `POST /api/chat` - Conversational medical assistant

### Web Interface
- `GET /` - Redirect to dashboard
- `GET /dashboard` - Main control center
- `GET /alert` - Emergency alert form (with IP geolocation)

##  AI Agent Workflow

### Sequential Processing Flow:
1. **Alert Creation** → Structured data capture
2. **Medical Analysis** → Severity scoring (1-5) & resource type
3. **Coordinator Decision** → Hospital selection using HospitalService
4. **Route Calculation** → Real ETA using ORSService  
5. **Hospital Preparation** → Bed reservation & team alert
6. **Clinical Protocols** → Specialist recommendations
7. **UI Consolidation** → Patient-friendly status updates

### Tool Integration:
- **HospitalSearchTool**: Bound to Coordinator Agent
- **RouteCalculationTool**: Bound to Ambulance Agent

##  Map Features

### Real-time Ambulance Tracking
- **Polyline Routes**: Actual road paths from ORS
- **Smooth Animation**: 60fps interpolated movement
- **Custom Icons**: Ambulance & hospital markers
- **Auto-fit Bounds**: Dynamic map centering

### Hospital Network
- **10 Major Facilities**: Covering Morocco's main cities
- **Specialty Filtering**: Emergency, Cardiology, Surgery, etc.
- **Distance Calculation**: Geodesic distance with traffic consideration

##  MediBot Capabilities

### Intelligent Conversations
- **Medical Knowledge**: Groq-powered responses
- **Emergency Detection**: Keywords trigger auto-redirect
- **Safety Guardrails**: Never replaces medical professionals
- **French Language**: Localized for Morocco

### Emergency Keywords:
- "douleur thoracique" → Immediate alert redirect
- "difficulté respirer" → Emergency protocol
- "perte de conscience" → Critical response

##  Production Considerations

### Security
- Environment variable configuration
- Firebase security rules
- API rate limiting (implement as needed)
- Input validation & sanitization

### Scalability
- Singleton Firebase service
- Background crew processing
- Real-time WebSocket potential
- Horizontal scaling ready

### Monitoring
- Crew execution logging
- Firebase real-time updates
- Error handling & fallbacks
- Performance metrics ready

##  UI/UX Design

### Professional Medical Theme
- **Dark Sidebar**: Medical professional aesthetic
- **Clean Cards**: White backgrounds with subtle shadows
- **Color Coding**: Red (emergency), Blue (info), Green (success)
- **Responsive**: Mobile-first design
- **Accessibility**: WCAG compliant structure

### Real-time Feedback
- **Toast Notifications**: System updates
- **Live Counters**: ETA timers
- **Status Indicators**: Pulsing animations
- **Progress Tracking**: Visual workflow states

##  Sample Data

The system includes realistic sample data for Morocco:
- **10 Major Hospitals**: From Casablanca to Marrakech
- **Specialty Coverage**: Emergency, Cardiology, Surgery, Neurology
- **Geographic Distribution**: Major cities covered
- **Coordinate Accuracy**: Real GPS locations

##  Deployment Ready

### Production Checklist
- ✅ Environment configuration
- ✅ Error handling & logging
- ✅ Database persistence
- ✅ Real-time capabilities
- ✅ Professional UI/UX
- ✅ API documentation
- ✅ Security considerations

### Next Steps for Production
1. Implement WebSocket for real-time updates
2. Add user authentication & authorization
3. Set up monitoring & alerting
4. Configure load balancing
5. Add comprehensive testing suite
6. Implement backup & disaster recovery

---

**MediAlert SMA v2.0** - Saving lives through intelligent emergency response. ❤️