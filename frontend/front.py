# -*- coding: utf-8 -*-

__author__ = 'ufian'

from flask import Flask, redirect, request, url_for, flash, session
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
    res = requests.get('http://localhost:8080/tweets')
    if session.get('twitter_user') and session.get('twitter_token'):
        l = link('logout', session['twitter_user'])
    else:
        l = link('login', 'Login')
    print res.json()
    return l + \
           u"<br>\n" + \
        u"\n".join(TEMPLATE.format(id=row['tweet_id']) for row in res.json()) + u'\n' + SCRIPT

