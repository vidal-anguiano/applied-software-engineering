from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Sequence, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Tickets(Base):
    __tablename__ = 'ticket_sales'

    t_id = Column('t_id', Integer, primary_key=True)
    dt_sold = Column('dt_sold', Date)
    dt_ride = Column('dt_ride', Date)
    rdr_nme = Column('rdr_nme', String)
    b_route = Column('b_route', String)
    status = Column('status', String)
    amnt_pd = Column('amnt_pd', Integer)
