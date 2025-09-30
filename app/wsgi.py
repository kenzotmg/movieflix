from . import create_app
app = create_app()   # gunicorn servirá "wsgi:app"
