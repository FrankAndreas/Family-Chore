from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class TestTask(Base):
    __tablename__ = 'test_tasks'
    id = Column(Integer, primary_key=True)
    req_ph = Column(Text, default="false")

# create in-memory db
engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

t = TestTask(req_ph=True)
db.add(t)
db.commit()

db.refresh(t)
print("STORED AS:", repr(t.req_ph))
