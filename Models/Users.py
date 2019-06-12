from sqlalchemy import Column, String, Integer
from Models.Model import Model


class Users(Model):
    __tablename__ = 'sv_users'
    __table_args__ = {"schema": "oncore"}
    contact_id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(String, nullable=False)
    active_user_flag = Column(String)

