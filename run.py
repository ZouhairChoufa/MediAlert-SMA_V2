import os
import sys
from app.crew.crew import SystemeUrgencesMedicalesCrew
from dotenv import load_dotenv

# Load environment variables from config directory
load_dotenv('config/.env')

from app import create_app

app = create_app()

if __name__ == '__main__':
    import sys
    sys.stdout.flush()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)