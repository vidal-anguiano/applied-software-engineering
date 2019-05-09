from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Sequence, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Tickets(Base):
    __tablename__ = 'ticket_sales'

    t_id = Column('t_id', Integer, primary_key=True)
    date_sold = Column('date_sold', Date)
    ride_date = Column('ride_date', Date)
    rider_name = Column('rider_name', String)
    bus_route = Column('bus_route', String)
    status = Column('status', String)
    amount_paid = Column('amount_paid', Integer)
