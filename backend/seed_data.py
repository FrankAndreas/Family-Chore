
from backend.database import SessionLocal
from backend.models import Role, User


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
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                print(f"Creating role: {role_data['name']}")
                new_role = Role(**role_data)
                db.add(new_role)
            else:
                print(f"Role {role_data['name']} already exists.")

        db.commit()

        # 2. Seed Admin User
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if admin_role:
            existing_user = db.query(User).filter(User.nickname == "Admin").first()
            if not existing_user:
                print("Creating default Admin user...")
                admin_user = User(
                    nickname="Admin",
                    login_pin="1234",
                    role_id=admin_role.id,
                    current_points=0,
                    lifetime_points=0
                )
                db.add(admin_user)
                db.commit()
                print("Admin user created.")
            else:
                print("Admin user already exists.")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
