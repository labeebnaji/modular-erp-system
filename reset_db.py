from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.infrastructure.database import Base, DATABASE_URL

# Import all models to ensure Base.metadata has knowledge of them
# This import is necessary for Base.metadata.create_all() to work correctly
from app.domain.models import *
from app.domain.settings_models import *


def reset_database():
    # Connect to the default 'postgres' database to drop/create erp_db
    # This assumes 'postgres' is the default database and user has permissions
    admin_database_url = DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    # Use isolation_level="AUTOCOMMIT" for admin operations like DROP/CREATE DATABASE
    admin_engine = create_engine(admin_database_url, isolation_level="AUTOCOMMIT")

    print(f"Attempting to connect to admin database: {admin_database_url}")
    try:
        with admin_engine.connect() as connection: # Use connection directly, not Session
            # Terminate all active connections to erp_db
            print("Terminating active connections to erp_db...")
            connection.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'erp_db'
                  AND pid <> pg_backend_pid();
            """))
            # No commit needed here because of AUTOCOMMIT isolation level

            # Drop the database if it exists
            print("Dropping database 'erp_db' if it exists...")
            connection.execute(text("DROP DATABASE IF EXISTS erp_db;"))
            print("Database 'erp_db' dropped.")

            # Create the database
            print("Creating database 'erp_db'...")
            connection.execute(text("CREATE DATABASE erp_db;"))
            print("Database 'erp_db' created.")
    except Exception as e:
        print(f"Error during database drop/create: {e}")
        print("Please ensure your PostgreSQL server is running and you have sufficient permissions.")
        return

    # Now connect to the newly created erp_db to create tables
    engine = create_engine(DATABASE_URL)
    print("Creating tables in 'erp_db'...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        print("Please check your model definitions and database connection.")

if __name__ == "__main__":
    reset_database()
