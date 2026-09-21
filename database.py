import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./ehmet.sqlite3')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://','postgresql://',1)
kwargs={}
if DATABASE_URL.startswith('sqlite'):
    kwargs['connect_args']={'check_same_thread':False}
engine=create_engine(DATABASE_URL,pool_pre_ping=True,**kwargs)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base=declarative_base()

class Assessment(Base):
    __tablename__='assessments'
    id=Column(Integer,primary_key=True)
    anonymous_id=Column(String(40),unique=True,nullable=False,index=True)
    created_at=Column(DateTime,nullable=False)
    age=Column(Integer); sex=Column(String(20)); weight=Column(Float); height=Column(Float); bmi=Column(Float); waist=Column(Float)
    sbp=Column(Float); dbp=Column(Float); smoking=Column(String(30)); antihypertensive=Column(Boolean); established_cvd=Column(Boolean)
    diabetes=Column(String(20)); diabetes_years=Column(Float); age_diabetes_dx=Column(Float); hba1c=Column(Float)
    total_chol=Column(Float); hdl=Column(Float); ldl=Column(Float); non_hdl=Column(Float); triglycerides=Column(Float); lipid_lowering=Column(Boolean)
    creatinine=Column(Float); egfr=Column(Float); ast=Column(Float); alt=Column(Float); platelets=Column(Float); ggt=Column(Float)
    fib4=Column(Float); fib4_category=Column(String(40)); fib4_version=Column(String(40))
    cv_algorithm=Column(String(60)); cv_risk=Column(Float); cv_risk_category=Column(String(30)); cv_risk_source=Column(String(120)); rcv_version=Column(String(50))
    site_code=Column(String(30)); professional_code=Column(String(30)); notes=Column(Text)

Base.metadata.create_all(bind=engine)
