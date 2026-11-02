from sqlalchemy.orm import Session
from app.db.database import engine, Base
from app.db.models import User
from app.core.security import get_password_hash
from app.core.config import settings
from app.core.logging import logger


def init_db(db: Session = None):
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")

    if db is not None:
        # Check if default admin exists
        admin = db.query(User).filter(User.email == settings.ADMIN_DEFAULT_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.ADMIN_DEFAULT_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
                full_name="CampusHelp Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            logger.info(f"Default admin user created: {settings.ADMIN_DEFAULT_EMAIL}")
        else:
            logger.info(f"Default admin user already exists: {settings.ADMIN_DEFAULT_EMAIL}")


if __name__ == "__main__":
    from app.db.database import SessionLocal
    with SessionLocal() as session:
        init_db(session)
