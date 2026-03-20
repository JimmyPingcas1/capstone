import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware  # <-- add this
from .db import init_db  # initialize MongoDB client

app = FastAPI(title="AI Water Quality System")

# --------------------------
# CORS Middleware (allow frontend requests)
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # <-- allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],       # <-- allow POST, GET, etc.
    allow_headers=["*"],       # <-- allow all headers
)

# Shared templates instance (absolute path to app/templates)
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize DB (connect to MongoDB)
init_db()

# Import routers after templates and init to avoid circular imports
from .routes import routers  # list of all routers

# Include all routers
for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    # Use uvicorn.run to avoid Windows multiprocessing issues
    uvicorn.run("app.server:app", host="127.0.0.1", port=5000, reload=True)