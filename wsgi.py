"""
WSGI Entry Point for Production Deployment.
Supports Gunicorn (Linux/macOS) and Waitress (Windows).
"""

import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'production')
application = create_app(env)
app = application  # alias for standard WSGI servers

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    try:
        from waitress import serve
        print(f"Starting production WSGI server (Waitress) on http://127.0.0.1:{port}...")
        serve(application, host='127.0.0.1', port=port)
    except ImportError:
        application.run(host='127.0.0.1', port=port)
