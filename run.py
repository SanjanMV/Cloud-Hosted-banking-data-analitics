import os
from app import create_app

# Set environment to development if not specified
if not os.getenv('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'

app = create_app()

if __name__ == '__main__':
    # Enable debug only in development
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=True)
