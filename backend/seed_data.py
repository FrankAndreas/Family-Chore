
import secrets
import logging
from backend.database import SessionLocal
from backend.models import Role, User
from backend import security

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

        # 2. Seed Admin User
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if admin_role:
            existing_user = db.query(User).filter(
                User.nickname == "Admin").first()
            if not existing_user:
                initial_pin = secrets.choice(
                    [str(i).zfill(4) for i in range(1000, 10000)
                     if len(set(str(i).zfill(4))) > 1 and str(i).zfill(4) != "1234"]
                )
                logger.warning(
                    f"Creating default Admin user. INITIAL PIN: {initial_pin} — change this immediately."
                )
                admin_user = User(
                    nickname="Admin",
                    login_pin=security.get_password_hash(initial_pin),
                    role_id=admin_role.id,
                    current_points=0,
                    lifetime_points=0
                )
                db.add(admin_user)
                db.commit()
                logger.info("Admin user created.")
            else:
                logger.info("Admin user already exists.")

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
