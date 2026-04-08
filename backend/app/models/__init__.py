from app.database import Base, engine
from app.models.blog import Blog

Base.metadata.create_all(bind=engine)