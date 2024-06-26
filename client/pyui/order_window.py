from PyQt5.QtWidgets import QMainWindow
from client.pyui.order_window_model import Ui_Form
from client.pyui.billing_window import BillingWindow
from client.pyui.realtor_window import RealtorWindow
from client.pyui.contract_window import ContractWindow
import json
import base64


class OrderWindowException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"OrderWindowException: {self.message}"


class OrderWindow(QMainWindow, Ui_Form):
    def __init__(self, login, order, server_api, callback, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.login = login
        self.server_api = server_api
        if 'id' not in order:
            raise OrderWindowException('invalid order params')
        self.order = order
        self.callback = callback
        if not (
                self.__get_order_info() and self.__get_billing_info() and self.__get_realtor_info() and self.__get_contract_info()):
            raise OrderWindowException('failed to get info about order')
        self.__init_ui()
        self.billingBtn.clicked.connect(self.__show_billing)
        self.realtorBtn.clicked.connect(self.__show_realtor)
        self.contractBtn.clicked.connect(self.__show_contract)

    def closeEvent(self, event):
        self.callback()
        event.accept()

    def __get_order_info(self):
        response = self.server_api.get_order(self.order['id'])
        if response is None or response.status_code != 200:
            return False
        try:
            json_resp = json.loads(response.text)
        except ValueError:
            return False
        self.order['client_id'] = json_resp['client_id']
        self.order['contract_id'] = json_resp['contract_id']
        self.order['realtor_id'] = json_resp['realtor_id']
        self.order['basic_info'] = json_resp['basic_info']
        self.order['order_number'] = json_resp['order_number']
        return True

    def __get_billing_info(self):
        response = self.server_api.get_billing(self.order['id'])
        if response is None or response.status_code != 200:
            return False
        try:
            json_resp = json.loads(response.text)
        except ValueError:
            return False
        self.billing = dict()
        self.billing['id'] = json_resp['id']
        self.billing['status'] = json_resp['status']
        self.billing['price'] = json_resp['price']
        self.billing['payment_date'] = json_resp['payment_date']
        return True

    def __get_realtor_info(self):
        response = self.server_api.get_realtor(self.order['realtor_id'])
        if response is None or response.status_code != 200:
            return False
        try:
            json_resp = json.loads(response.text)
        except ValueError:
            return False
        self.realtor = dict()
        self.realtor['id'] = json_resp['id']
        self.realtor['full_name'] = json_resp['full_name']
        self.realtor['phone_number'] = json_resp['phone_number']
        self.realtor['rating'] = json_resp['rating']
        self.realtor['experience'] = json_resp['experience']
        self.realtor['photo'] = base64.b64decode(json_resp['photo'])
        self.realtor['responses'] = json_resp['responses']
        return True

    def __get_contract_info(self):
        response = self.server_api.get_contract(self.order['contract_id'])
        if response is None or response.status_code != 200:
            return False
        try:
            json_resp = json.loads(response.text)
        except ValueError:
            return False
        self.contract = dict()
        self.contract['id'] = json_resp['id']
        self.contract['reg_number'] = json_resp['reg_number']
        self.contract['contract_number'] = json_resp['contract_number']
        self.contract['details'] = json_resp['details']
        return True

    def __show_billing(self):
        billing_wnd = BillingWindow(self.billing, self)
        billing_wnd.show()

    def __show_realtor(self):
        realtor_wnd = RealtorWindow(self.realtor, self.login, self.server_api, self)
        realtor_wnd.show()

    def __show_contract(self):
        contract_wnd = ContractWindow(self.contract, self)
        contract_wnd.show()

    def __init_ui(self):
        self.orderNumberLbl.setText(f'Заказ №{self.order["order_number"]}')

        self.commonInfoTextEdit.setPlainText(self.order['basic_info'])
        self.commonInfoTextEdit.setReadOnly(True)

        self.statusLineEdit.setText(self.order['status'])
        self.statusLineEdit.setReadOnly(True)

        self.billingLineEdit.setText(str(self.billing['price']))
        self.billingLineEdit.setReadOnly(True)

        self.realtorLineEdit.setText(self.realtor['full_name'])
        self.realtorLineEdit.setReadOnly(True)

        self.contractLineEdit.setText(str(self.contract['contract_number']))
        self.contractLineEdit.setReadOnly(True)
