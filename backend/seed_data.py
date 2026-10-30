
import logging
from backend.database import SessionLocal
from backend.models import Role

logger = logging.getLogger(__name__)


def seed_data():
    db = SessionLocal()
    try:
        # 1. Seed Roles
        roles = [
            {"name": "Admin", "multiplier_value": 1.0},
            {"name": "Contributor", "multiplier_value": 1.0},
            {"name": "Teenager", "multiplier_value": 1.2},
            {"name": "Child", "multiplier_value": 1.5},
        ]

        for role_data in roles:
            existing_role = db.query(Role).filter(
                Role.name == role_data["name"]).first()
            if not existing_role:
                logger.info(f"Creating role: {role_data['name']}")
                new_role = Role(**role_data)
                db.add(new_role)
            else:
                logger.info(f"Role {role_data['name']} already exists.")

        db.commit()

        # No people here: they come from the family hub (spec 2026-10-30), parents as Admin

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
