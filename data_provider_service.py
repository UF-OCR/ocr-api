from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models import init_database
from Models import Protocols
from Models import LogDetail
from Models import Users
import logging
import os


logging.basicConfig(filename=os.environ.get('log_file', None), level=logging.DEBUG)

class DataProviderService:
    def __init__(self, engine):
        """
        :param engine: The engine route and login details
        :return: a new instance of DAL class
        :type engine: string
        """
        if not engine:
            raise ValueError('The values specified in engine parameter has to be supported by SQLAlchemy')
        self.engine = engine
        db_engine = create_engine(engine)
        db_session = sessionmaker(bind=db_engine)
        self.session = db_session()

    def init_database(self):
        """
        Initializes the database tables and relationships
        :return: None
        """
        init_database(self.engine)

    def get_protocols(self):
        """
        Loads all the protocols

        :return: The protocol_no.
        """
        all_protocols = self.session.query(Protocols.protocol_no,Protocols.title).all()

        return all_protocols

    def log_details(self, user_name, ip_address, call_time, validated):
        """

               Creates and saves logFiles to the database.

               :param user_name: user name recorded from the request
               :param ip_address: ip address of the user
               :param call_time: request call time
               :param validated: record if user was validated

               """
        new_log_detail = LogDetail(
            user_name=user_name,
            call_time=call_time,
            ip_address=ip_address,
            validated=validated
        )
        self.session.add(new_log_detail)
        self.session.commit()

        return new_log_detail.log_details_id

    def get_user(self, user_name):
        """
              If the user name parameter is  defined then it looks up the user in oncore table

              :param user_name: The id of the user
              :return: The user details.
              """
        if user_name:
            user = self.session.query(Users).filter(user_name == Users.user_id).first()
            return user
        else:
            return None



