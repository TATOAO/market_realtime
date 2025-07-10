from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Stock Monitor Backend",
    description="Backend service for stock monitoring and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Stock Monitor Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stock_monitor_backend"}

# Import and include other routers here as they are developed
# from .core.center import router as center_router
# app.include_router(center_router, prefix="/api/v1")
