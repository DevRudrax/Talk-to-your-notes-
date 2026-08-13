import sys
import os

# Add backend folder to sys.path so app module can be loaded by Vercel Serverless
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.main import app

# Export ASGI handler for Vercel
app = app
