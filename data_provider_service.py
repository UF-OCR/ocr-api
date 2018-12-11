from sqlalchemy import create_engine
import cx_Oracle
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.properties')

oracle_connection_string = (
        'oracle+cx_oracle://{username}:{password}@' +
        cx_Oracle.makedsn('{hostname}', '{port}', sid='{sid}')
)

engine = create_engine(
    oracle_connection_string.format(
        username=config.get('DatabaseSection', 'username'),
        password=config.get('DatabaseSection', 'password'),
        hostname=config.get('DatabaseSection', 'hostname'),
        port=config.get('DatabaseSection', 'port'),
        sid=config.get('DatabaseSection', 'sid')
    )
)
