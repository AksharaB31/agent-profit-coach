import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your models from the project
sys.path.append(os.path.abspath("."))
from app.infra.mysql.models import Booking, BookingFlight, BookingSegment, BookingAdjustedFare
from app.core.config import settings

# --- CONFIGURATION ---
DB_URL = "mysql+pymysql://root:@localhost:3307/afineagent" 
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_data():
    db = SessionLocal()
    
    print("--- Database Verification ---")
    
    # 1. Total Bookings
    total_bookings = db.query(Booking).count()
    print(f"Total Bookings in DB: {total_bookings}")
    
    # 2. Total Flights
    total_flights = db.query(BookingFlight).count()
    print(f"Total Flights in DB: {total_flights}")
    
    # 3. Total Segments
    total_segments = db.query(BookingSegment).count()
    print(f"Total Segments in DB: {total_segments}")
    
    # 4. Route Stats (WAW -> BER for sup_f8a1)
    from sqlalchemy import func
    result = db.query(
        func.count(Booking.id).label("total_bookings"),
        func.sum(func.if_(func.upper(Booking.status).in_(['CONFIRMED', 'COMPLETED', 'TICKETED', 'SUCCESS']), 1, 0)).label("successful_bookings")
    ).join(
        BookingFlight, Booking.id == BookingFlight.booking_id
    ).join(
        BookingSegment, BookingFlight.id == BookingSegment.booking_flight_id
    ).filter(
        Booking.provider == "sup_f8a1",
        BookingSegment.departure_airport == "WAW",
        BookingSegment.arrival_airport == "BER"
    ).first()
    
    print(f"Route WAW->BER for sup_f8a1: Total={result.total_bookings}, Success={result.successful_bookings}")
    
    # 5. Commission Stats
    comm_result = db.query(
        func.avg(BookingAdjustedFare.agent_profit).label("avg_agent_profit")
    ).join(
        Booking, Booking.id == BookingAdjustedFare.booking_id
    ).filter(
        Booking.provider == "sup_f8a1"
    ).first()
    
    print(f"Average Profit for sup_f8a1: {comm_result.avg_agent_profit}")
    
    db.close()

if __name__ == "__main__":
    verify_data()
