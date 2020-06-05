#Whats-Pplaying Shows what are you playing now in spotify

from flask import Flask, request, redirect
import urllib.parse
import requests
import json
import secrets

app = Flask(__name__)

scopes = 'user-read-currently-playing'
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
        'grant_type': 'authorization_code',
        'code': request.args.get('code'),
        'redirect_uri': redirect_url,
        'client_id' : my_client_id,
        'client_secret' : my_client_secret
    }

    req = requests.post(spotify_token, data=data)

    return json.loads(req.text)['access_token']

if __name__ == '__main__':
    app.debug = True
    app.run()