
'''

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
FLASK_APP=flask_backend.py python3 -m flask run --host=0.0.0.0 --port=3012
FLASK_APP=flask_backend.py python3 -m flask run --host=0.0.0.0 --port=3112

'''

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS, cross_origin
from random import randint
import json

import threading
import time
import os
import io
import requests

import db_base
import accounts
import constants

class FlaskServer(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskServer, self).__init__(*args, **kwargs)
        self.accounts = accounts.accounts()
        # using a subdirectory here, hosted on <>.com/port/<api>
        # so can be customised via constants
        if constants.dev_mode:
            self.subDir = constants.flask_dev_subdir
        else:
            self.subDir = constants.flask_prod_subdir


app = FlaskServer(__name__)
CORS(app, support_credentials=True)


@app.route(app.subDir + '/')
@app.route('/index')
@cross_origin(supports_credentials=True)
def index():
    return "Flask Root page."


@app.route(app.subDir + '/api/is-logged-in', methods=['POST'])
@cross_origin(supports_credentials=True)
def is_logged_in():
    request.form = json.loads(request.get_data().decode('utf-8'))
    name = request.form['name']
    session_uuid = request.form['uuid']

    ret_val = app.accounts.active_sessions.check_session(name, session_uuid)
    return jsonify(ret_val)


@app.route(app.subDir + '/api/get-data', methods=['POST'])
@cross_origin(supports_credentials=True)
def get_data():
    request.form = json.loads(request.get_data().decode('utf-8'))
    name = request.form['name']
    session_uuid = request.form['uuid']
    data_name = request.form['data_name']
    # print(app.accounts.active_sessions.check_session(name, session_uuid))
    data = app.accounts.get_data(name, session_uuid, data_name)
    if data:
        return jsonify(data)
    else:
        return jsonify("")


@app.route(app.subDir + '/api/set-data', methods=['POST'])
@cross_origin(supports_credentials=True)
def set_data():
    request.form = json.loads(request.get_data().decode('utf-8'))
    name = request.form['name']
    session_uuid = request.form['uuid']
    data_name = request.form['data_name']
    data_value = request.form['data_value']
    append = str(request.form['append']).lower() == "true"
    toggle = str(request.form['toggle']).lower() == "true"

    delimiter = "<>"
    new_data = data_value
    cur_data = app.accounts.get_data(
        name, session_uuid, data_name
    )
    # print(cur_data)
    if not cur_data:
        # If cur_data isnt set, the make it blank to avoid
        # NoneType errors
        cur_data = ""
    final_data = ""
    if append:
        # If we're appending, need to use the delimiter
        new_data = delimiter + new_data
        # If the delimiter isnt at the start, then add it
        # bug that comes from swapping between append being true/false
        if cur_data.find(delimiter) != 0:
            cur_data = delimiter + cur_data
        if new_data in cur_data:
            if toggle:
                # If we have the new data in current, replace it with ""
                final_data = cur_data.replace(new_data, "")
            else:
                # If we don't want to toggle it, then just keep the
                # current data without adding the new data
                final_data = cur_data
        else:
            # If we don't have the new data in current,
            # then we want to just add it
            final_data = cur_data + new_data
    else:
        # If append isn't set, the just replace the data
        # or toggle if needed
        if toggle and new_data in cur_data:
            # If we're toggling, *and* new data is already in current
            # then just set the final data to blank (e.g wipe it)
            final_data = ""
        else:
            # If we're not toggling and don't already have the data
            # then just save the new data
            final_data = new_data

    # Finally, save the final data
    # print(name, session_uuid, data_name, final_data)
    result = app.accounts.set_data(
        name, session_uuid, data_name, final_data)
    if result:
        # print(final_data)
        # return jsonify(final_data)
        return jsonify(result)
    else:
        # print(result)
        return jsonify(result)


@app.route(app.subDir + '/api/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
    request.form = json.loads(request.get_data().decode('utf-8'))
    name = request.form['name']
    password = request.form['password']
    password_conf = request.form['password_conf']

    # If get_account is false, then we already have an account
    # with the given name. a return of 'None' would be no account found
    if app.accounts.get_account(name, "") is False:
        return "Account name already exists"
    elif password == password_conf:
        app.accounts.add_account(name, password)
        session = app.accounts.start_session(name, password)
    else:
        session = None

    if session:
        return str(session)
    else:
        return "Account/Password not valid"


@app.route(app.subDir + '/api/login', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def login():
    request.form = json.loads(request.get_data().decode('utf-8'))
    name = request.form['name']
    password = request.form['password']

    session = app.accounts.start_session(name, password)
    # print(app.accounts.active_sessions.check_session(name, session))
    if session:
        return str(session)
    else:
        return "Account/Password not valid"


@app.route(app.subDir + '/api/logout', methods=['POST'])
@cross_origin(supports_credentials=True)
def logout():
    request.form = json.loads(request.get_data().decode('utf-8'))
    name = request.form['name']
    session_uuid = request.form['uuid']

    return jsonify(app.accounts.end_session(name, session_uuid))
