import os
import sys

from a2wsgi import ASGIMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.chdir(BASE_DIR)

from main import app as fastapi_app

application = ASGIMiddleware(fastapi_app)
