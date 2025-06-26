from datetime import date, timedelta
from app.database.config import SessionLocal, engine
from app.models.models import Base, Service
from app.services import crud

def init_database():
    """Initialize database with sample data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if services already exist
        existing_services = crud.get_services(db)
        if existing_services:
            print("Services already exist. Skipping initialization.")
            return
        
        # Create sample services
        services = [
            {
                "name": "Làm móng gel",
                "description": "Làm móng gel cơ bản với sơn gel chất lượng cao",
                "duration_minutes": 60,
                "price": 200000
            },
            {
                "name": "Làm móng gel kèm vẽ",
                "description": "Làm móng gel với thiết kế vẽ nghệ thuật theo yêu cầu",
                "duration_minutes": 90,
                "price": 350000
            },
            {
                "name": "Sơn móng thường",
                "description": "Sơn móng với sơn thường, khô nhanh",
                "duration_minutes": 30,
                "price": 100000
            },
            {
                "name": "Cắt và dũa móng",
                "description": "Dịch vụ cắt, dũa và chăm sóc móng cơ bản",
                "duration_minutes": 20,
                "price": 50000
            },
            {
                "name": "Làm móng đính đá",
                "description": "Làm móng gel kèm đính đá và phụ kiện trang trí",
                "duration_minutes": 120,
                "price": 500000
            },
            {
                "name": "Tẩy và làm lại móng",
                "description": "Tẩy móng cũ và làm móng mới hoàn toàn",
                "duration_minutes": 90,
                "price": 400000
            }
        ]
        
        for service_data in services:
            service = Service(**service_data)
            db.add(service)
        
        db.commit()
        print(f"Created {len(services)} services successfully!")
        
        # Generate time slots for the next 7 days
        today = date.today()
        for i in range(7):
            target_date = today + timedelta(days=i)
            slots = crud.generate_time_slots(db, target_date)
            print(f"Generated {len(slots)} time slots for {target_date}")
        
        print("Database initialization completed!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()