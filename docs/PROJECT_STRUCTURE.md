# MediAlert Pro v2.0 - Project Structure

## Directory Organization

```
medialert_pro/
├── app/                          # Main application code
│   ├── crew/                     # AI Agent orchestration
│   │   ├── config/              # Agent & task configurations
│   │   │   ├── agents.yaml      # 7-agent definitions
│   │   │   └── tasks.yaml       # Sequential workflow tasks
│   │   ├── crew_simple.py       # Simplified crew implementation
│   │   ├── crew.py              # Full CrewAI implementation
│   │   └── tools.py             # Custom CrewAI tools
│   ├── routes/                   # Flask endpoints
│   │   ├── api.py               # REST API endpoints
│   │   ├── chat.py              # MediBot conversations
│   │   └── web.py               # Dashboard & forms
│   ├── services/                 # Core business logic
│   │   ├── firebase_service.py  # Real-time data persistence
│   │   ├── hospital_service.py  # CSV loading & spatial search
│   │   ├── location_service.py  # IP-based geolocation
│   │   └── ors_service.py       # Route calculation & polylines
│   ├── static/                   # Frontend assets
│   │   ├── assets/              # Icons & images
│   │   ├── css/                 # Custom styles
│   │   ├── images/              # Application images
│   │   └── js/                  # JavaScript modules
│   │       ├── dashboard.js     # Real-time UI updates
│   │       └── map_animation.js # Ambulance tracking logic
│   ├── templates/                # HTML templates
│   │   ├── components/          # Reusable UI components
│   │   │   └── chat_widget.html # MediBot chat interface
│   │   ├── base.html            # Professional layout
│   │   └── dashboard.html       # Main control center
│   ├── __init__.py              # Flask app factory
│   └── config.py                # Application configuration
├── config/                       # Configuration files
│   ├── .env                     # Environment variables (private)
│   ├── .env.example             # Environment template
│   └── firebase-credentials.json # Firebase service account (private)
├── data/                         # Data files
│   └── morocco_hospitals.csv    # Hospital database
├── deployment/                   # Deployment configurations
│   └── docker-compose.yml       # Container orchestration
├── docs/                         # Documentation
│   ├── PROJECT_STRUCTURE.md     # This file
│   └── README.md                # Main documentation
├── logs/                         # Application logs
├── scripts/                      # Utility scripts
│   ├── install.py               # Installation script
│   ├── requirements.txt         # Full dependencies
│   ├── requirements_fixed.txt   # Working dependencies
│   └── requirements_minimal.txt # Minimal dependencies
├── tests/                        # Test files
│   ├── test_installation.py     # Installation verification
│   └── test_simple.py           # Simple component tests
├── .gitignore                    # Git ignore rules
├── Dockerfile                    # Container definition
└── run.py                        # Application entry point
```

## Key Components

### Application Core (`app/`)
- **Flask App Factory Pattern**: Modular, scalable architecture
- **Blueprint Organization**: Separate concerns (API, Web, Chat)
- **Service Layer**: Business logic abstraction
- **Template System**: Professional UI components

### AI Engine (`app/crew/`)
- **7-Agent Workflow**: Sequential emergency response processing
- **YAML Configuration**: Declarative agent and task definitions
- **Tool Integration**: Hospital search and route calculation
- **Groq Integration**: Advanced language model processing

### Configuration (`config/`)
- **Environment Management**: Secure API key storage
- **Firebase Setup**: Real-time database configuration
- **Development/Production**: Environment-specific settings

### Data Management (`data/`)
- **Hospital Database**: Morocco medical facilities
- **Geospatial Data**: Coordinates and specialties
- **CSV Format**: Easy maintenance and updates

### Deployment (`deployment/`)
- **Docker Support**: Containerized deployment
- **Production Ready**: Nginx reverse proxy
- **Scalable Architecture**: Multi-container setup

### Testing (`tests/`)
- **Installation Verification**: Component testing
- **Integration Tests**: End-to-end validation
- **Simple Tests**: Quick health checks

## File Naming Conventions

- **Python Files**: `snake_case.py`
- **Configuration**: `lowercase.extension`
- **Templates**: `lowercase.html`
- **Static Assets**: `kebab-case.js/css`
- **Documentation**: `UPPERCASE.md`

## Security Considerations

- **Environment Variables**: Sensitive data in `config/.env`
- **Firebase Credentials**: Service account in `config/`
- **Git Ignore**: Prevents credential exposure
- **Docker Secrets**: Production credential management

## Development Workflow

1. **Setup**: Run `scripts/install.py`
2. **Configuration**: Update `config/.env`
3. **Testing**: Run `tests/test_simple.py`
4. **Development**: `python run.py`
5. **Deployment**: `docker-compose up`

This structure follows enterprise software development best practices with clear separation of concerns, security considerations, and deployment readiness.