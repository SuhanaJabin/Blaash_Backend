from database import Base,engine
from models import User

print("Creating database now...")

Base.metadata.create_all(engine)