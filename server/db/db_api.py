import logging

from dotenv import load_dotenv
import os
import pyodbc
from server.db.request_checker import only_letters_digits_dash, only_printed_chars


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class DBHandler:
    def __init__(self):
        self.sql_requests = {
            'authorize':    'SELECT role FROM agency_system.dbo.users WHERE login=\'{login}\' AND \
                            password_hash=\'{password_hash}\'',
            'get_billings': 'SELECT b.* \
                            FROM agency.dbo.billings b \
                            INNER JOIN agency.dbo.billings_orders bo ON b.id = bo.billing_id \
                            INNER JOIN agency.dbo.orders o ON bo.order_id = o.id \
                            INNER JOIN agency.dbo.clients c ON o.client_id = c.id \
                            WHERE c.login = \'{login}\'',
            'get_orders': 'SELECT o.* \
                            FROM agency.dbo.orders o \
                            INNER JOIN agency.dbo.clients c ON o.client_id = c.id \
                            WHERE c.login = \'{login}\'',
            'get_order': 'SELECT * FROM agency.dbo.orders WHERE id = CAST(\'{id}\' AS uniqueidentifier)',
            'get_billing': 'SELECT b.* \
                            FROM agency.dbo.billings b \
                            JOIN agency.dbo.billings_orders bo ON b.id = bo.billing_id \
                            WHERE bo.order_id = CAST(\'{id}\' as uniqueidentifier)',
            'get_realtor': 'SELECT * FROM agency.dbo.realtors WHERE id = CAST(\'{id}\' AS uniqueidentifier)',
            'get_contract': 'SELECT * FROM agency.dbo.contracts WHERE id = CAST(\'{id}\' AS uniqueidentifier)',
            'add_response': 'DECLARE @RESPONSE_ID uniqueidentifier; SET @RESPONSE_ID = NEWID(); INSERT agency.dbo.responses VALUES (@RESPONSE_ID, \'Отзыв от {login}: {message}\'); INSERT agency.dbo.responses_realtors VALUES (CAST(\'{realtor_id}\' as uniqueidentifier), @RESPONSE_ID)',
            'get_response': 'SELECT r.message \
                            FROM agency.dbo.responses r \
                            JOIN agency.dbo.responses_realtors rr ON r.id = rr.response_id \
                            WHERE rr.realtor_id = CAST(\'{realtor_id}\' as uniqueidentifier)',
            'get_profile': 'SELECT * FROM agency.dbo.clients WHERE login = \'{login}\''
        }

    def init(self, path_to_env_file):
        self.__read_env(path_to_env_file)

    def __read_env(self, path_to_env_file):
        load_dotenv(path_to_env_file)
        self.conn = pyodbc.connect(driver=os.getenv('DB_DRIVER'),
                                   server=os.getenv('DB_SERVER'),
                                   database=os.getenv('DB_NAME'),
                                   uid='admin',
                                   pwd='admin',
                                   trusted_connection='yes')

    def __execute(self, request, fields, checker=only_letters_digits_dash, need_commit=False):
        # check for sql injections
        if checker is not None:
            for field in fields:
                if not checker(field):
                    logging.error(f'attempt to substitute in the field {field}')
                    return None
        cursor = self.conn.cursor()
        res = cursor.execute(request)
        if need_commit:
            cursor.commit()
        return res

    def authorize(self, login, password_hash):
        return self.__execute(self.sql_requests['authorize'].format(login=login, password_hash=password_hash),
                              [login, password_hash])

    def get_billings(self, login):
        return self.__execute(self.sql_requests['get_billings'].format(login=login), [login])

    def get_orders(self, login):
        return self.__execute(self.sql_requests['get_orders'].format(login=login), [login])

    def get_order(self, order_id):
        return self.__execute(self.sql_requests['get_order'].format(id=order_id), [order_id])

    def get_billing(self, billing_id):
        return self.__execute(self.sql_requests['get_billing'].format(id=billing_id), [billing_id])

    def get_realtor(self, realtor_id):
        return self.__execute(self.sql_requests['get_realtor'].format(id=realtor_id), [realtor_id])

    def get_contract(self, contract_id):
        return self.__execute(self.sql_requests['get_contract'].format(id=contract_id), [contract_id])

    def add_response(self, login, message, realtor_id):
        return self.__execute(self.sql_requests['add_response'].format(login=login, message=message, realtor_id=realtor_id),
                              [login, message, realtor_id], None, True)

    def get_responses(self, realtor_id):
        return self.__execute(self.sql_requests['get_response'].format(realtor_id=realtor_id), [realtor_id])

    def get_profile(self, login):
        return self.__execute(self.sql_requests['get_profile'].format(login=login), [login])

    def close(self):
        self.conn.close()
