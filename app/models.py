from sqlalchemy.sql.expression import text
from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer, String,Boolean, TIMESTAMP, ForeignKey, ARRAY

# with sqlalchemy we can create database using python code and 
# we do not need to create DB tables manually. So we can focus on logic of the api more.

# "posts" table is created in the database using below constraints
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, nullable=False, primary_key=True)
    todo = Column(String, nullable=False)
    completed = Column(Boolean, nullable=False, server_default='False')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default = text('now()'))
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    category = Column(Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    # user = relationship("User")

# "users" table is created in the database using below constraints
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    fullname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default = text('now()') )

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, nullable=False, primary_key=True)
    category = Column(String, nullable=False, server_default="miscellaneous")
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    isShared = Column(Boolean, nullable=False, server_default="False")
    # sharedWith = Column(ARRAY(Integer), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default = text('now()') )

class ShareTable(Base):
    __tablename__ = "shared_table"
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False, primary_key=True)
    category_id = Column(Integer,ForeignKey("category.id",ondelete="CASCADE"), nullable=False, primary_key=True)
    