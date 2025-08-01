from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import our custom modules
from app.routes import recommendation_router
from app.auth_routes import auth_router
from app.saved_items_routes import saved_items_router
from app.gemini_routes import gemini_router
from app.database import create_tables

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Litflix API",
    version="1.0.0",
    debug=os.getenv("DEBUG", "False").lower() == "true"
)

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(recommendation_router, prefix="/api", tags=["recommendations"])
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(saved_items_router, prefix="/api/saved", tags=["saved_items"])
app.include_router(gemini_router, prefix="/api/gemini", tags=["gemini"])

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to Litflix API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )


