from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper, relationship
from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP, func, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

db_engine = "postgresql+psycopg2://postgres:1122334455@localhost:5433/wf_brokers_account"
engine = create_engine(db_engine)
Base = declarative_base()

class TrackingDaily(Base):
    __tablename__ = "tracking_daily"  # Tên bảng

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_logs = Column(JSON, nullable=True)  # JSONB column
    account_id = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    broker_name = Column(Text, nullable=False)
    platform_name = Column(Text, nullable=False)
    deals = relationship("HistoryDealsSeries", back_populates="tracking_daily", cascade="all, delete-orphan")

    def to_dict(self):
        """
        Convert the SQLAlchemy object to a dictionary.
        """
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

    def __repr__(self):
        return f"<TrackingDailyAccount(id={self.id}, broker_name={self.broker_name}, platform_name={self.platform_name})>"
    
class HistoryDealsSeries(Base):
    __tablename__ = "history_deals_series"  # Tên bảng

    id = Column(Integer, primary_key=True, autoincrement=True)
    deal_logs = Column(JSON, nullable=True)  # JSONB column
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)

    tracking_daily_id = Column(Integer, ForeignKey('tracking_daily.account_id'), nullable=False)
    
    tracking_daily = relationship("TrackingDaily", back_populates="deals")

    def to_dict(self):
        """
        Convert the SQLAlchemy object to a dictionary.
        """
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

    def __repr__(self):
        return f"<TrackingDailyAccount(id={self.id}, broker_name={self.broker_name}, platform_name={self.platform_name})>"

# db_engine = "<dialect>+<driver>://<username>:<password>@<host>:<port>/<db_name>"
# Tạo session
Base.metadata.create_all(engine)
