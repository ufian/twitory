# -*- coding: utf-8 -*-

__author__ = 'ufian'

import os.path
import requests

from flask import url_for, request, session, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict


from app import app, config
from oauth import require_oauth

app.secret_key = config['flask']['private']
app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/', endpoint="index")
def index():
    data = dict()
    
    if session.get('twitter_user') and session.get('twitter_token'):
        data['user'] = session.get('twitter_user')
        res = requests.get(config['twitory']['backend'], params={'user': data['user']})
        result = res.json()
        if result.get("status", "error") == "ok":
            data['tweets'] = result['tweets']
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
