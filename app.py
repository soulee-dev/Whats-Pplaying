#Whats-Pplaying Shows what are you playing now in spotify
#DB setting email(varchar, 30) uuid(char, 36), access_token(varchar, 180), refresh_token(varchar, 180), expires_in(int, 4), recent_granted(timestamp)
import datetime

from flask import Flask, request, redirect, send_file
import urllib.parse
import requests
import json
import uuid
from dbModule import DataBase
import secrets
from image import PlayerImage

app = Flask(__name__)

scopes = 'user-read-playback-state user-read-email'
redirect_url = 'http://118.44.195.217:5000/callback'
spotify_auth = 'https://accounts.spotify.com/authorize'
spotify_token = 'https://accounts.spotify.com/api/token'
my_client_id = secrets.my_client_id
my_client_secret = secrets.my_client_secret

def sendRequest(uri, access_token):
    headers = {
        'Authorization': 'Bearer ' + access_token
    }

    return requests.get(uri, headers=headers)

@app.route('/login')
def login():
    return redirect(spotify_auth + '?response_type=code' +
      '&client_id=' + my_client_id + '&scope=' + urllib.parse.quote(scopes) +
      '&redirect_uri=' + urllib.parse.quote(redirect_url))

@app.route('/callback')
def callback():

    #Initialize mysql

    data = {
        'grant_type' : 'authorization_code',
        'code': request.args.get('code'),
        'redirect_uri': redirect_url,
        'client_id' : my_client_id,
        'client_secret' : my_client_secret
    }

    req = requests.post(spotify_token, data=data)
    data = json.loads(req.text)

    unique_id = str(uuid.uuid4())
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_in = str(data['expires_in'])

    req = sendRequest('https://api.spotify.com/v1/me', access_token)
    email = json.loads(req.text)['email']

    sql = 'SELECT * FROM customers WHERE email=%s'

    with DataBase() as db:
        result = db.excuteAll(sql, (email, ))

    if len(result) < 1:
        sql = "INSERT INTO customers(email, uuid, access_token, refresh_token, expires_in) VALUES (%s, %s, %s, %s, %s)"
        val = (email, unique_id, access_token, refresh_token, expires_in)

        with DataBase() as db:
            db.commit(sql, val)


        return unique_id

    return result[0][1]

@app.route('/player-status')
def playerStatus():

    sql = 'SELECT * FROM customers WHERE uuid=%s'

    with DataBase() as db:
        result = db.excuteAll(sql, (request.args.get('token'),))

    if len(result) < 1:
        return 'There is no data!'

    req = sendRequest('https://api.spotify.com/v1/me/player', result[0][2])

    if req.status_code == 204:
        return 'There is no playing content.'

    pi = PlayerImage()

    data = json.loads(req.text)

    image_uri = data['item']['album']['images'][0]['url']
    progress_ms = data['progress_ms']
    duration_ms = data['item']['duration_ms']
    name = data['item']['name']
    artist = data['item']['album']['artists'][0]['name']

    filepath = pi.createImage(image_uri=image_uri, progress_ms=progress_ms, duration_ms=duration_ms, name=name, artist=artist)

    return send_file(filepath, mimetype='image/png')

@app.route('/refresh-token')
def refreshToken():

    sql = 'SELECT * FROM customers WHERE uuid=%s'

    with DataBase() as db:
        result = db.excuteAll(sql, (request.args.get('token'),))

    #Exit when no data
    if len(result) < 1:
        return 'There is no data!'

    print(result[0][3])

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': result[0][3],
        'client_id': my_client_id,
        'client_secret': my_client_secret
    }

    req = requests.post(spotify_token, data=data)

    data = json.loads(req.text)

    sql = 'UPDATE customers SET access_token=%s, recent_granted=%s WHERE uuid=%s'
    val = (data['access_token'], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request.args.get('token'))

    with DataBase() as db:
        db.commit(sql, val)

    return 'New access token granted!'


if __name__ == '__main__':

    PRODUCTION_MODE = False

    if PRODUCTION_MODE:
        print('Production mode')
        app.debug = False
        app.run()

    elif not PRODUCTION_MODE:
        print('Develop mode')
        app.debug = True
        app.run(host='0.0.0.0')
