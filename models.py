from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

# Define the SQLite database engine
engine = create_engine('sqlite:///databases/test.db')

# Define the base class for our Expense model
Base = declarative_base()

# Define the Expense model class
class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    price = Column(Float)
    usage = Column(String)
    date = Column(Date)
    category = Column(String)

    def __init__(self, price, usage, date, category):
        self.price = price
        self.usage = usage
        self.date = date
        self.category = category

# Create the database tables (if not already created)
Base.metadata.create_all(engine)
