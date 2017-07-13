# -*- coding: utf-8 -*-

__author__ = 'ufian'

from flask import redirect, request, url_for, flash, session
import functools
from flask_oauth import OAuth

from app import app, config

oauth = OAuth()

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=config['twitter']['consumer_key'],
    consumer_secret=config['twitter']['consumer_secret']
)

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')

@app.route('/oauth-authorized', )
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)


@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('twitter_user', None)
    session.pop('twitter_token', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))

def require_oauth(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('twitter_user') or not session.get('twitter_token'):
            return redirect(url_for('login', next=request.url))

        return fn(*args, **kwargs)
    return wrapper