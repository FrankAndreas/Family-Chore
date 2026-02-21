import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.database import SessionLocal, engine
from backend import models

# Get a real session
db = SessionLocal()

# Check what's in the DB for requires_photo_verification
tasks = db.query(models.Task).all()
for t in tasks:
    print(f"Task {t.id}: name={t.name}, requires_photo_verification={repr(t.requires_photo_verification)}")
