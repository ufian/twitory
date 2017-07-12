# -*- coding: utf-8 -*-

__author__ = 'ufian'

from flask import Flask, redirect, request, url_for, flash, session, render_template
import requests
import json
import yaml
from flask_oauth import OAuth
from app import app, config
from oauth import login, logout, oauth_authorized

TEMPLATE = u'''<blockquote class="twitter-tweet" data-lang="en"><p lang="ru" dir="ltr"><a href="https://twitter.com/gimlis/status/{id}">__</a></blockquote>'''
SCRIPT = u'''<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'''

app.secret_key = config['flask']['private']
app.config['SESSION_TYPE'] = 'filesystem'


def link(endpoint, title):
    return "<a href='{url}'>{title}</a>".format(
        url=url_for(endpoint),
        title=title
    )

@app.route('/')
def index():
    data = dict()
    
    if session.get('twitter_user') and session.get('twitter_token'):
        data['user'] = session.get('twitter_user')
        res = requests.get('http://localhost:8080/tweets', params={'user': data['user']})
        data['tweets'] = res.json()
    else:
        data['user'] = None

    return render_template('index.html', **data)
