
from end_point.app import application
import os

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=os.environ.get('FLASK_APP_PORT'),use_reloader=False)
