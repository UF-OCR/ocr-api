import os
from sqlalchemy import Column, String, Integer
from models.Model import Model

class DiseaseDiagnosis(Model):
    __tablename__ = 'sv_pcl_disease_diagnosis'
    __table_args__ = {"schema": os.environ.get('ORACLE_CURRENT_SCHEMA', None)}
    protocol_id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String, nullable=False)
