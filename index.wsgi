
import logging
import sys
sys.path.append('/home/d/denmb//wordpress_2/public_html/')
sys.path.append('/home/d/denmb/myenv/lib/python3.6/site-packages/')

from app import create_app

logging.basicConfig(stream=sys.stderr)
app = create_app()
application = app

if __name__ == '__main__':
    app.run()