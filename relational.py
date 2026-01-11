from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(String, unique=True)  # Linked to your Auth provider (Clerk/Firebase)
    integrations = relationship("Integration", back_populates="artist")
    metrics = relationship("MetricLog", back_populates="artist")


class Integration(Base):
    __tablename__ = 'integrations'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'))
    platform_name = Column(String)  # 'spotify', 'apple', 'manual_csv'
    access_token = Column(String)  # Encrypted
    refresh_token = Column(String)  # Encrypted
    last_synced = Column(DateTime, default=datetime.datetime.utcnow)
    artist = relationship("Artist", back_populates="integrations")


class MetricLog(Base):
    """The Normalized Data Store"""
    __tablename__ = 'metric_logs'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'))
    timestamp = Column(DateTime, index=True)

    # Normalized Fields
    total_listeners = Column(Integer)  # Unified: Spotify Monthly + Apple Unique
    total_streams = Column(Integer)
    revenue_estimate = Column(Float)

    # Raw Data (for safety)
    raw_json_data = Column(JSON)

    artist = relationship("Artist", back_populates="metrics")