from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.session import create_tables
from .api.routes import auth, classes, lessons, assignments, grading, recommendations, gradebook

app = FastAPI(
    title="K12 LMS API",
    description="A modern learning management system for K-12 education",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(classes.router, prefix="/api/classes", tags=["classes"])
app.include_router(lessons.router, prefix="/api/lessons", tags=["lessons"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["assignments"])
app.include_router(grading.router, prefix="/api/grading", tags=["grading"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(gradebook.router, prefix="/api/gradebook", tags=["gradebook"])


@app.get("/")
async def root():
    return {"message": "Welcome to K12 LMS API"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
