# Virtual Environment Setup - MediAlert Pro v2.0

## What Was Done

### 1. Removed Global Dependencies
- Uninstalled all globally installed packages to avoid conflicts
- Cleaned up system Python environment

### 2. Created Virtual Environment
```bash
python -m venv .venv
```

### 3. Installed Dependencies in Virtual Environment
```bash
.venv\Scripts\activate
pip install -r scripts\requirements_fixed.txt
```

### 4. Created Activation Scripts

#### `activate_venv.bat`
- Activates virtual environment
- Opens command prompt in activated state

#### `start_app.bat`
- Activates virtual environment
- Sets PYTHONPATH
- Starts Flask application

## How to Use

### Option 1: Manual Activation
```bash
# Activate virtual environment
.venv\Scripts\activate

# Set Python path
set PYTHONPATH=.

# Run application
python run.py
```

### Option 2: Using Batch Scripts
```bash
# Just activate environment
activate_venv.bat

# Start application directly
start_app.bat
```

### Option 3: PowerShell (Alternative)
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Set Python path
$env:PYTHONPATH = "."

# Run application
python run.py
```

## Installed Packages

The virtual environment contains only the necessary packages:

- **flask==3.0.0** - Web framework
- **firebase-admin==6.4.0** - Database integration
- **openrouteservice==2.3.3** - Route calculation
- **requests==2.31.0** - HTTP client
- **python-dotenv==1.0.0** - Environment variables
- **groq==0.4.1** - AI language model
- **pandas==2.1.4** - Data manipulation
- **geopy==2.4.1** - Geographic calculations
- **polyline==2.0.0** - Route encoding/decoding
- **pydantic==2.12.5** - Data validation
- **langchain-core==0.2.43** - LangChain core
- **langchain-groq==0.1.9** - Groq integration

## Benefits

### ✅ **Isolated Environment**
- No conflicts with system packages
- Clean dependency management
- Reproducible setup

### ✅ **Version Control**
- Exact package versions locked
- Consistent across environments
- Easy deployment

### ✅ **Security**
- No global package pollution
- Controlled dependency scope
- Safe development environment

## Verification

Test the setup:
```bash
.venv\Scripts\activate
set PYTHONPATH=.
python tests\test_simple.py
```

Expected output:
```
[OK] Flask
[OK] Pandas
[OK] Geopy
[OK] Groq
[OK] LangChain Groq
[OK] Hospital Service
[OK] MediAlert Crew
[OK] Flask App Created

[SUCCESS] All components working!
```

## Troubleshooting

### Issue: "No module named 'app'"
**Solution:** Set PYTHONPATH before running:
```bash
set PYTHONPATH=.
```

### Issue: Virtual environment not activating
**Solution:** Use full path:
```bash
c:\path\to\medialert_pro\.venv\Scripts\activate.bat
```

### Issue: Permission denied (PowerShell)
**Solution:** Enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Development Workflow

1. **Start Development:**
   ```bash
   start_app.bat
   ```

2. **Install New Package:**
   ```bash
   .venv\Scripts\activate
   pip install package_name
   pip freeze > scripts\requirements_updated.txt
   ```

3. **Update Dependencies:**
   ```bash
   .venv\Scripts\activate
   pip install -r scripts\requirements_fixed.txt --upgrade
   ```

The virtual environment ensures a clean, isolated, and reproducible development environment for MediAlert Pro v2.0.