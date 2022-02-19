from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, UniqueConstraint, JSON, Numeric, DATE
from sqlalchemy.sql.expression import text

from managers.dal.sqlalchemy import Base


class StockName(Base):
    __tablename__ = "stock_names"

    id = Column(Integer, primary_key=True, nullable=True)
    stock_name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))


class PriceAction(Base):
    __tablename__ = "price_actions"

    id = Column(Integer, primary_key=True, nullable=True)
    stock_id = Column(Integer, ForeignKey("stock_names.id"), nullable=False)
    hour_1_start = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_1_end = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_2_start = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_2_end = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_3_start = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_3_end = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_4_start = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_4_end = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_5_start = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_5_end = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_6_start = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_6_end = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_7_start = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    hour_7_end = Column(Numeric(10, 2), nullable=False, server_default=text('0.0'))
    price_date = Column(DATE, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))
    __table_args__ = (UniqueConstraint('stock_id', 'price_date', name='_stock_price_date_uc'),)


class ShortlistedStock(Base):
    __tablename__ = "shortlisted_stocks"

    id = Column(Integer, primary_key=True, nullable=True)
    stock_id = Column(Integer, ForeignKey("stock_names.id"), nullable=False)
    price_action_ids = Column(JSON, nullable=False)
    conditions_met_on = Column(DATE, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))
    __table_args__ = (UniqueConstraint('stock_id', 'conditions_met_on', name='_shortlisted_date_uc'),)