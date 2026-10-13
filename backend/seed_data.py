
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

        # 2. Seed the first Admin user, only while no user has the Admin role,
        # so a renamed or deleted default Admin doesn't come back on restart
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if admin_role:
            existing_admin = db.query(User).filter(
                User.role_id == admin_role.id).first()
            if not existing_admin:
                initial_pin = secrets.choice(
                    [str(i).zfill(4) for i in range(1000, 10000)
                     if len(set(str(i).zfill(4))) > 1 and str(i).zfill(4) != "1234"]
                )
                # "Admin" may still exist as a non-admin user (e.g. demoted); pick a free name
                nickname = "Admin"
                suffix = 2
                while db.query(User).filter(User.nickname == nickname).first():
                    nickname = f"Admin{suffix}"
                    suffix += 1
                logger.warning(
                    f"Creating default admin user '{nickname}'. INITIAL PIN: {initial_pin} — change this immediately."
                )
                admin_user = User(
                    nickname=nickname,
                    login_pin=security.get_password_hash(initial_pin),
                    role_id=admin_role.id,
                    current_points=0,
                    lifetime_points=0
                )
                db.add(admin_user)
                db.commit()
                logger.info("Admin user created.")
            else:
                logger.info("An admin user already exists, not creating the default Admin.")

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
