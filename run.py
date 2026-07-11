import os
import sys

# Add the project root to the sys.path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app import create_app, socketio
from app.logging_config import configure_logging

app = create_app()
configure_logging(app)

if __name__ == '__main__':
    # For local development, run the Flask development server directly with SocketIO
    socketio.run(app, debug=True, port=5000)
