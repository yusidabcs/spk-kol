import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Support persistent volume on cloud hosting (Railway: /data, default local: current dir)
DB_PATH = os.environ.get("DB_PATH", "./spk_kol.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class KolKandidat(Base):
    __tablename__ = "kol_kandidat"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nama_lengkap = Column(String)
    niche = Column(String, index=True)
    bio = Column(Text)
    followers = Column(Integer)
    avg_likes = Column(Float)
    avg_comments = Column(Float)
    engagement_rate = Column(Float)
    posting_consistency = Column(Integer)
    content_quality_score = Column(Float)
    niche_relevance = Column(Float)
    instagram_url = Column(String)

class Kriteria(Base):
    __tablename__ = "kriteria"
    id = Column(Integer, primary_key=True)
    kode = Column(String, unique=True)
    nama = Column(String)
    bobot_default = Column(Float)
    satuan = Column(String)
    deskripsi = Column(Text)

class SesiKalkulasi(Base):
    __tablename__ = "sesi_kalkulasi"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    filter_niche = Column(String, default="Semua")
    filter_min_followers = Column(Integer, default=0)
    filter_max_followers = Column(Integer, default=999999)
    bobot_json = Column(JSON)
    jumlah_kandidat = Column(Integer)

class HasilRanking(Base):
    __tablename__ = "hasil_ranking"
    id = Column(Integer, primary_key=True)
    id_sesi = Column(Integer, index=True)
    id_kol = Column(Integer, index=True)
    username = Column(String)
    niche = Column(String)
    followers = Column(Integer)
    skor_total = Column(Float)
    posisi = Column(Integer)
    kontribusi_c1 = Column(Float)
    kontribusi_c2 = Column(Float)
    kontribusi_c3 = Column(Float)
    kontribusi_c4 = Column(Float)
    kontribusi_c5 = Column(Float)
    r_c1 = Column(Float)
    r_c2 = Column(Float)
    r_c3 = Column(Float)
    r_c4 = Column(Float)
    r_c5 = Column(Float)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
