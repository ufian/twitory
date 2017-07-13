# -*- coding: utf-8 -*-

__author__ = 'ufian'

from flask import Flask
import yaml

app = Flask(__name__)

def load_config(path='config.yaml'):
    with open(path, 'r') as f:
        return yaml.load(f.read())

config = load_config()
