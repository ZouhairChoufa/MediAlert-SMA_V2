# 🚀 MediAlert SMA - Setup Guide

## Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone https://github.com/your-username/medialert-sma.git
cd medialert-sma
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r scripts/requirements_fixed.txt
```

### 5. Configure Environment Variables
```bash
# Copy example file
copy config\.env.example config\.env

# Edit config/.env with your API keys
```

**Required API Keys:**
- **Groq API**: Get free key at https://console.groq.com
- **OpenRouteService**: Get free key at https://openrouteservice.org/dev/#/signup
- **AbstractAPI**: Get free key at https://www.abstractapi.com/api/ip-geolocation-api

### 6. Run Application
**Windows:**
```bash
start_app.bat
```

**Manual:**
```bash
set PYTHONPATH=.
python run.py
```

### 7. Access Application
- **Home**: http://localhost:5000
- **Dashboard**: http://localhost:5000/dashboard
- **Create Alert**: http://localhost:5000/alert

## 🔑 API Keys Setup

### Groq API (AI Models)
1. Visit https://console.groq.com
2. Sign up for free account
3. Generate API key
4. Add to `config/.env`: `GROQ_API_KEY=your_key_here`

### OpenRouteService (Routing)
1. Visit https://openrouteservice.org/dev/#/signup
2. Create free account
3. Generate API key
4. Add to `config/.env`: `ORS_API_KEY=your_key_here`

### AbstractAPI (IP Geolocation)
1. Visit https://www.abstractapi.com/api/ip-geolocation-api
2. Sign up for free plan (20,000 requests/month)
3. Get API key
4. Add to `config/.env`: `ABSTRACT_API_KEY=your_key_here`

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in run.py
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r scripts/requirements_fixed.txt --force-reinstall
```

### API Key Errors
- Check `config/.env` file exists
- Verify API keys are correct
- Ensure no extra spaces in keys

## 📦 Project Structure
```
medialert_pro/
├── app/
│   ├── crew/              # AI agents
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── static/            # CSS, JS, data
│   └── templates/         # HTML pages
├── config/                # Configuration
├── data/                  # Hospital data
├── scripts/               # Utility scripts
└── run.py                 # Application entry
```

## 🎯 Next Steps
1. Test MediBot chat
2. Create emergency alert
3. View live tracking
4. Explore dashboard

## 📞 Support
- GitHub Issues: https://github.com/your-username/medialert-sma/issues
- Documentation: See README.md
