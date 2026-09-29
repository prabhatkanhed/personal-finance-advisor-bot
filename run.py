import os
from app import create_app

# Instantiate Flask application
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    print(f"Starting Personal Finance Advisor Bot on http://127.0.0.1:{port} (Debug: {debug})...")
    app.run(host='127.0.0.1', port=port, debug=debug)
