from backend.app.database import Base

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class DailyRate(Base):
    __tablename__ = 'daily_rates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    rate = Column(Float, nullable=False)


class Sale(Base):
    __tablename__ = 'sale'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_hour = Column(DateTime, nullable=False)
    total_usd = Column(Float, nullable=False)
    rate_used = Column(Float, nullable=False)
    payments = relationship('Pay', backref='sale',
                            cascade='all, delete-orphan')


class Pay(Base):
    __tablename__ = 'pay'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sale.id'), nullable=False)
    method = Column(String, nullable=False)
    native_amount = Column(Float, nullable=False)
    equivalent_usd_amount = Column(Float, nullable=False)
