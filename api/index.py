import sys
import os

# Resolve backend and root paths for Vercel Serverless Function environment
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
backend_dir = os.path.abspath(os.path.join(current_dir, "../backend"))

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app

try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = app

# Export handler for Vercel serverless runtime
app = handler


