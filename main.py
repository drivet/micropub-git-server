import os
from micropub import app as application


# for Flask-IndieAuth
application.config['ME'] = os.environ['ME']
application.config['TOKEN_ENDPOINT'] = os.environ['TOKEN_ENDPOINT']
# application.config['TESTING'] = True

if __name__ == "__main__":
    application.run()
