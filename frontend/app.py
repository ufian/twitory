# -*- coding: utf-8 -*-

__author__ = 'ufian'

from flask import Flask, session
import yaml

app = Flask(__name__)

def load_config(path='config.yaml'):
    with open(path, 'r') as f:
        return yaml.load(f.read())

config = load_config()

@app.before_request
def make_session_permanent():
    session.permanent = True
