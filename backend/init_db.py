"""
Database Initialization Script
Creates database tables and optionally seeds with sample data.
"""
import sys
import argparse
from app.database import engine, Base, SessionLocal
from app.models import device, task

def init_database(seed=False):
    """
    Initialize the database.

    Args:
        seed: If True, add sample data
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

    if seed:
        print("\nSeeding database with sample data...")
        seed_database()
        print("✓ Database seeded successfully")

def seed_database():
    """Add sample data to database"""
    from app.models.device import Device, DeviceVendor, DeviceStatus

    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Device).count() > 0:
            print("  Database already contains data, skipping seed")
            return

        # Sample devices
        devices = [
            Device(
                name="fw-main",
                vendor=DeviceVendor.MIKROTIK,
                model="RB4011",
                ip_address="192.168.1.1",
                mac_address="AA:BB:CC:DD:EE:01",
                status=DeviceStatus.PENDING,
                ssh_username="admin",
                ssh_password="admin",  # Change in production!
                ssh_port=22,
                check_in_method="http",
                check_in_interval=300,
            ),
            Device(
                name="fw-branch",
                vendor=DeviceVendor.FORTINET,
                model="FortiGate 60E",
                ip_address="192.168.2.1",
                mac_address="AA:BB:CC:DD:EE:02",
                status=DeviceStatus.PENDING,
                ssh_username="admin",
                ssh_password="admin",
                ssh_port=22,
                check_in_method="http",
                check_in_interval=300,
            ),
            Device(
                name="sw-main",
                vendor=DeviceVendor.UBIQUITI,
                model="USW-24-POE",
                mac_address="AA:BB:CC:DD:EE:03",
                status=DeviceStatus.PENDING,
                api_url="https://unifi.example.com:8443",
                ssh_username="admin",
                ssh_password="admin",
                check_in_method="controller",
                check_in_interval=300,
                metadata={"unifi_site": "default"}
            ),
            Device(
                name="fw-guest",
                vendor=DeviceVendor.WATCHGUARD,
                model="Firebox T35",
                ip_address="192.168.3.1",
                mac_address="AA:BB:CC:DD:EE:04",
                status=DeviceStatus.PENDING,
                ssh_username="admin",
                ssh_password="admin",
                ssh_port=22,
                check_in_method="ssh",
                check_in_interval=600,
            ),
        ]

        for dev in devices:
            db.add(dev)
            print(f"  Added device: {dev.name} ({dev.vendor.value})")

        db.commit()

    except Exception as e:
        print(f"  Error seeding database: {str(e)}", file=sys.stderr)
        db.rollback()
        raise
    finally:
        db.close()

def drop_all():
    """Drop all database tables"""
    print("WARNING: This will delete all data!")
    response = input("Are you sure you want to drop all tables? (yes/no): ")
    if response.lower() == "yes":
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped")
    else:
        print("Operation cancelled")

def main():
    parser = argparse.ArgumentParser(description="Initialize OrcheNet database")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed database with sample data"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (DESTRUCTIVE)"
    )

    args = parser.parse_args()

    try:
        if args.drop:
            drop_all()

        init_database(seed=args.seed)
        print("\n✓ Database initialization complete!")

    except Exception as e:
        print(f"\n✗ Database initialization failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
