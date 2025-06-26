import uvicorn
from init_data import init_database

if __name__ == "__main__":
    # Initialize database with sample data
    print("Initializing database...")
    init_database()
    
    # Run the FastAPI application
    print("Starting FastAPI server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )