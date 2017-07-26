# -*- coding: utf-8 -*-

__author__ = 'ufian'

import os.path
import requests
from collections import OrderedDict
from datetime import datetime

from flask import url_for, request, session, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict


from app import app, config
from oauth import require_oauth

app.secret_key = config['flask']['private']
app.config['SESSION_TYPE'] = 'filesystem'


def get_year_title(tweet):
    timestamp = tweet['timestamp'][:-6]
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    delta = datetime.now().year - dt.year
    
    if delta == 0:
        return 'Today'
    elif delta == 1:
        return 'Year ago'
    else:
        return '{0} years ago'.format(delta)

@app.route('/', endpoint="index")
def index():
    data = dict()
    
    if session.get('twitter_user') and session.get('twitter_token'):
        data['user'] = session.get('twitter_user')
        res = requests.get(config['twitory']['backend'], params={'user': data['user']})
        result = res.json()
        if result.get("status", "error") == "ok":
            tweets = OrderedDict()
            for tweet in result['tweets']:
                key = tweet['timestamp'].split()[0]
                if key not in tweets:
                    tweets[key] = list()
                tweets[key].append(tweet)
                
            data['header_links'] = OrderedDict()
            data['tweet_years'] = OrderedDict()
            
            for key, key_tweets in tweets.items():
                data['header_links']['#{0}'.format(key)] = get_year_title(key_tweets[0])
                data['tweet_years'][key] = get_year_title(key_tweets[0])

            data['tweets'] = tweets
        else:
            data['error'] = result.get('error', 'Error on request')
    else:
        data['user'] = None

    return render_template('index.html', **data)


class UploadForm(FlaskForm):
    tweetsfile = FileField('tweets.csv', validators=[FileRequired()])

@app.route('/upload', methods=['GET', 'POST'])
@require_oauth
def upload():
    data = dict()
    data['user'] = session.get('twitter_user')
    
    form = UploadForm(CombinedMultiDict((request.files, request.form)))

    if form.validate_on_submit():
        f = form.tweetsfile.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            config['twitory']['archive'], '{0}.csv'.format(data['user'])
        ))
        return render_template('upload_success.html', **data)

    return render_template('upload.html', form=form, **data)
