import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import your models from the project 
from app.infra.mysql.models import (
    Base, Agent, Supplier, Markup, Booking, BookingAdjustedFare, 
    BookingProcess, BookingFlight, BookingSegment
)
from app.core.config import settings

# --- CONFIGURATION ---
DB_URL = "mysql+pymysql://root:@localhost:3307/afineagent"

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        print("Starting Enhanced Database Seeder for Agent Profit Coach...")

        # 0. Clean existing data to ensure no overlapping zero values
        print("Cleaning old data...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.query(BookingAdjustedFare).delete()
        db.query(BookingSegment).delete()
        db.query(BookingFlight).delete()
        db.query(BookingProcess).delete()
        db.query(Booking).delete()
        db.query(Markup).delete()
        db.query(Supplier).delete()
        db.query(Agent).delete()
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.commit()

        # 1. Seed Agents (No nulls)
        print("Seeding Agents...")
        agent1 = Agent(
            user_id=1, parent_id=1, email="agent2@gmail.com", establishment_name="Agent 2 Establishment",
            director_name="Director 1", nature_of_business="Travel", cr_number="CR123",
            cr_expiry_date=datetime.utcnow() + timedelta(days=365), vat_number="VAT123",
            street="123 Agent St", country="Australia", state="Queensland", city="Allora",
            province="QLD", office_telephone="123456789", office_email="office@agent2.com",
            bank_name="Bank of Aus", bank_branch="Main", account_number="ACC123", iban="IBAN123",
            manager_name="Manager 1", manager_email="mgr@agent2.com", manager_mobile="123456789",
            finance_name="Finance 1", finance_email="fin@agent2.com", finance_mobile="123456789",
            ticketing_contact="ticketing@agent2.com", holidays_contact="holidays@agent2.com",
            annual_volume_words="One Million", annual_volume_figures="1000000",
            agent_type="B2B", business_type="Corporate", recommended_by="System",
            onboarding_submitted_at=datetime.utcnow(), is_active=True,
            approval_status="approved", created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        db.add(agent1)
        db.commit()
        agent_id = agent1.id if agent1.id else 1

        # 2. Seed Suppliers (Including EVERY supplier seen in JSON payloads)
        print("Seeding Suppliers...")
        suppliers_data = [
            {"code": "sup_k2m7", "name": "K2M7 Aviation", "health_status": "healthy"},
            {"code": "sup_f8a1", "name": "F8A1 Logistics", "health_status": "healthy"},
            {"code": "sup_x9p4", "name": "GetFares", "health_status": "healthy"},
            {"code": "sup_t6v3", "name": "TravelSky", "health_status": "healthy"},
            {"code": "sup_q7d2", "name": "OneFly", "health_status": "healthy"}
        ]
        for sup in suppliers_data:
            db.add(Supplier(code=sup["code"], name=sup["name"], health_status=sup["health_status"], 
                            is_active=True, last_checked_at=datetime.utcnow()))
        db.commit()

        # 3. Seed Markups
        print("Seeding Markups...")
        airlines = ["BA", "QR", "LO", "SK", "LH", "OS"]
        for airline in airlines:
            db.add(Markup(
                owner_type="global", owner_id=1, supplier_code="ALL", airline_code=airline,
                origin="ALL", destination="ALL", cabin_class="Economy",
                markup_type="PERCENTAGE", markup_value=random.uniform(2.0, 5.0), 
                priority=1, status="active"
            ))
        db.commit()

        # 4. Seed 1000 Bookings, Adjusted Fares, and Processes (No Nulls, No Zeros)
        print("Seeding 1,000 Bookings & Historical Data for all routes...")
        historical_suppliers = [s["code"] for s in suppliers_data]
        
        for i in range(1000):
            sup_code = random.choice(historical_suppliers)
            airline = random.choice(airlines)
            
            outcome = random.choices(
                ["SUCCESS", "CANCELLED", "REFUNDED", "FAILED"], 
                weights=[0.65, 0.15, 0.10, 0.10], 
                k=1
            )[0]
            
            status = "CONFIRMED" if outcome == "SUCCESS" else outcome
            total_amount = random.uniform(800.0, 2500.0)
            
            # Booking with all fields populated, no nulls
            booking = Booking(
                booking_ref_id=str(uuid.uuid4()),
                invoice_number=f"INV-{i}-{random.randint(1000, 9999)}",
                pnr=f"PNR{random.randint(1000, 9999)}",
                supplier_pnr=f"SPNR{random.randint(1000, 9999)}",
                booking_ref=f"REF-{i}-{random.randint(1000, 9999)}",
                trace_id=str(uuid.uuid4()),
                provider=sup_code,
                status=status,
                refundable=random.choice([True, False]),
                fare_type="Publish",
                currency="PLN",
                total_amount=total_amount,
                warnings='["none"]',
                booked_at=datetime.utcnow() - timedelta(days=random.randint(1, 100)),
                agent_id=agent_id,
                user_id=1,
                booking_date=datetime.utcnow() - timedelta(days=random.randint(1, 100)),
                last_ticketing_date=datetime.utcnow() + timedelta(days=1),
                hold_date=datetime.utcnow() - timedelta(days=1),
                issue_date=datetime.utcnow(),
                owner="system",
                passenger_count=1
            )
            db.add(booking)
            db.flush() 
            
            # Flight with all fields populated
            flight = BookingFlight(
                booking_id=booking.id,
                purchase_id=str(uuid.uuid4())[:15],
                flight_pnr=f"FPNR{random.randint(1000, 9999)}",
                validating_airline=airline,
                adult_count=1,
                child_count=0,
                infant_count=0,
                currency="PLN",
                current_status="PENDING",
                refundable=random.choice([True, False]),
                fare_type="Publish",
                ticket_time_limit=datetime.utcnow() + timedelta(days=1),
                fop="CC",
                sequence=1
            )
            db.add(flight)
            db.flush()
            
            # Segment with all fields populated
            routes = [("WAW", "BER"), ("DEL", "DXB"), ("DEL", "COK"), ("JFK", "LHR")]
            origin, destination = random.choice(routes)
            
            segment = BookingSegment(
                booking_flight_id=flight.id,
                airline=airline,
                flight_number=f"{airline}{random.randint(100, 999)}",
                cabin_class="Economy",
                fare_basis="Y",
                departure_airport=origin,
                arrival_airport=destination,
                departure_time=datetime.utcnow() + timedelta(days=random.randint(10, 30)),
                arrival_time=datetime.utcnow() + timedelta(days=random.randint(10, 30), hours=2),
                departure_terminal="1",
                arrival_terminal="2",
                duration_minutes=random.randint(60, 180),
                stop_over=False,
                aircraft_code="737",
                codeshare=False,
                operating_airline=airline,
                sequence=1,
                marketing_carrier=airline,
                trip_indicator="Outbound"
            )
            db.add(segment)
            
            # Process with all fields populated, no nulls
            process_state = "COMPLETED" if outcome == "SUCCESS" else outcome
            process = BookingProcess(
                id=str(uuid.uuid4()),
                user_id=1,
                provider_code=sup_code,
                state=process_state,
                current_step="BookStep",
                context='{"step": "BookStep"}',
                supplier_context='{"supplier": "ok"}',
                error_context='{"error": "none"}',
                idempotency_key=str(uuid.uuid4()),
                trace_id=str(uuid.uuid4()),
                wallet_hold_id=str(uuid.uuid4()),
                attempts=1,
                last_transition_at=datetime.utcnow()
            )
            db.add(process)
            
            # Fare with all fields populated, NO ZERO VALUES
            profit = random.uniform(25.0, 150.0) if outcome == "SUCCESS" else random.uniform(5.0, 15.0)
            fare = BookingAdjustedFare(
                booking_id=booking.id,
                total_amount=total_amount,
                total_tax=total_amount * 0.2,
                total_base=total_amount * 0.8,
                per_pax_base=total_amount * 0.8,
                markup_amount=profit,
                discount_amount=1.0, 
                supplier_commission=2.0, 
                admin_markup=5.0,
                agent_markup=profit,
                service_fee=1.0, 
                final_price=total_amount + profit + 5.0,
                final_total_base=total_amount * 0.8,
                admin_profit=5.0,
                agent_profit=profit,
                currency="PLN"
            )
            db.add(fare)

        db.commit()
        print("Database seeding completed successfully! Inserted 1,000 rich historical records.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
