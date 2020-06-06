#Whats-Pplaying Shows what are you playing now in spotify

from flask import Flask, request, redirect
import urllib.parse
import requests
import json
import uuid
import redis
import secrets

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

app = Flask(__name__)

scopes = 'user-read-playback-state'
redirect_url = 'http://localhost:5000/callback'
spotify_auth = 'https://accounts.spotify.com/authorize'
spotify_token = 'https://accounts.spotify.com/api/token'
my_client_id = secrets.my_client_id
my_client_secret = secrets.my_client_secret

@app.route('/login')
def login():
    return redirect(spotify_auth + '?response_type=code' +
      '&client_id=' + my_client_id + '&scope=' + urllib.parse.quote(scopes) +
      '&redirect_uri=' + urllib.parse.quote(redirect_url))

@app.route('/callback')
def callback():
    data = {
        'grant_type' : 'authorization_code',
        'code': request.args.get('code'),
        'redirect_uri': redirect_url,
        'client_id' : my_client_id,
        'client_secret' : my_client_secret
    }

    req = requests.post(spotify_token, data=data)
    unique_id = str(uuid.uuid4())

    r.set(unique_id, json.loads(req.text)['access_token'])

    return unique_id + ' ' + json.loads(req.text)['access_token']

@app.route('/player-status')
def playerStatus():

    headers = {
        'Authorization': 'Bearer ' + r.get(request.args.get('token'))
    }

    req = requests.get('https://api.spotify.com/v1/me/player', headers=headers)

    return req.text

if __name__ == '__main__':
    app.debug = True
    app.run()