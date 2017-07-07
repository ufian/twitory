# -*- coding: utf-8 -*-

__author__ = 'ufian'

TEMPLATE = u'''<blockquote class="twitter-tweet" data-lang="en"><p lang="ru" dir="ltr"><a href="https://twitter.com/gimlis/status/{id}">__</a></blockquote>'''
SCRIPT = u'''<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'''

from flask import Flask
import requests
import json
app = Flask(__name__)

@app.route('/')
def hello_world():
    res = requests.get('http://localhost:8080/tweets')
    return u"\n".join(TEMPLATE.format(id=row['Id']) for row in res.json()) + u'\n' + SCRIPT