from flask import Flask, make_response, request
from server.db.db_api import DBHandler
import json
import base64

app = Flask(__name__)


class HttpsServer:
    def __init__(self, cert_path, key_path):
        self.cert_path = cert_path
        self.key_path = key_path

    def run(self):
        app.run(host='0.0.0.0', port=443, ssl_context=(self.cert_path, self.key_path))


@app.route('/authorize', methods=['POST'])
def authorize():
    if 'login' not in request.form:
        return make_response('login field not found', 404)
    if 'password' not in request.form:
        return make_response('password field not found', 404)
    res = DBHandler().authorize(request.form['login'], request.form['password']).fetchone()
    if res is None:
        return make_response('invalid credentials', 403)
    out = {
        'role': res[0].strip()
    }
    return make_response(json.dumps(out), 200)


@app.route('/billings', methods=['GET'])
def get_billings():
    if 'login' not in request.args:
        return make_response('login field not found', 404)
    res = DBHandler().get_billings(request.args['login'])
    if res is None:
        return make_response('invalid fields in request', 404)
    out = list()
    for row in res:
        out.append({
            'id': row[0],
            'status': row[1],
            'price': row[2],
            'payment_date': row[3].strftime("%Y-%m-%d %H:%M:%S")
        })
    return make_response(json.dumps(out), 200)


@app.route('/orders', methods=['GET'])
def get_orders():
    if 'login' not in request.args:
        return make_response('login field not found', 404)
    res = DBHandler().get_orders(request.args['login'])
    if res is None:
        return make_response('invalid fields in request', 404)
    out = list()
    for row in res:
        order = {
            'id': row[0],
            'status': row[6],
            'start_date': row[7].strftime("%Y-%m-%d %H:%M:%S")
        }
        if row[8] is not None:
            order['end_date'] = row[8].strftime("%Y-%m-%d %H:%M:%S")
        out.append(order)
    return make_response(json.dumps(out), 200)


@app.route('/order', methods=['GET'])
def get_order():
    if 'id' not in request.args:
        return make_response('id field not found', 404)
    res = DBHandler().get_order(request.args['id']).fetchone()
    if res is None:
        return make_response('invalid fields in request', 404)

    order = {
        'id': res[0],
        'order_number': res[1],
        'client_id': res[2],
        'contract_id': res[3],
        'realtor_id': res[4],
        'basic_info': res[5],
        'status': res[6],
        'start_date': res[7].strftime("%Y-%m-%d %H:%M:%S")
    }
    if res[8] is not None:
        order['end_date'] = res[8].strftime("%Y-%m-%d %H:%M:%S")
    return make_response(json.dumps(order), 200)


@app.route('/billing', methods=['GET'])
def get_billing():
    if 'id' not in request.args:
        return make_response('id field not found', 404)
    res = DBHandler().get_billing(request.args['id']).fetchone()
    if res is None:
        return make_response('invalid fields in request', 404)

    billing = {
        'id': res[0],
        'status': res[1],
        'price': res[2]
    }
    if res[3] is not None:
        billing['payment_date'] = res[3].strftime("%Y-%m-%d %H:%M:%S")
    return make_response(json.dumps(billing), 200)


@app.route('/realtor', methods=['GET'])
def get_realtor():
    if 'id' not in request.args:
        return make_response('id field not found', 404)
    res = DBHandler().get_realtor(request.args['id']).fetchone()
    if res is None:
        return make_response('invalid fields in request', 404)

    realtor = {
        'id': res[0],
        'phone_number': res[1],
        'rating': res[2],
        'experience': res[3],
        'full_name': res[4],
        'photo': base64.encodebytes(res[5]).decode('utf-8'),
        'responses': list()
    }
    res = DBHandler().get_responses(request.args['id'])
    if res is None:
        return make_response('invalid fields in request', 404)
    for response in res:
        realtor['responses'].append(response[0])
    return make_response(json.dumps(realtor), 200)


@app.route('/contract', methods=['GET'])
def get_contract():
    if 'id' not in request.args:
        return make_response('id field not found', 404)
    res = DBHandler().get_contract(request.args['id']).fetchone()
    if res is None:
        return make_response('invalid fields in request', 404)

    realtor = {
        'id': res[0],
        'reg_number': res[1],
        'contract_number': res[2],
        'details': res[3]
    }
    return make_response(json.dumps(realtor), 200)


@app.route('/response', methods=['POST'])
def add_response():
    if 'login' not in request.form:
        return make_response('login field not found', 404)
    if 'message' not in request.form:
        return make_response('message field not found', 404)
    if 'realtor_id' not in request.form:
        return make_response('realtor_id field not found', 404)
    DBHandler().add_response(request.form['login'], request.form['message'], request.form['realtor_id'])
    return make_response('OK', 200)


@app.route('/profile', methods=['GET'])
def get_profile():
    if 'login' not in request.args:
        return make_response('login field not found', 404)
    res = DBHandler().get_profile(request.args['login']).fetchone()
    if res is None:
        return make_response('invalid fields in request', 404)

    profile = {
        'full_name': res[1],
        'phone_number': res[2],
        'login': res[3],
        'photo': base64.encodebytes(res[4]).decode('utf-8')
    }
    return make_response(json.dumps(profile), 200)
