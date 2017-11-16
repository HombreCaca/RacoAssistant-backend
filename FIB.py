from urllib import request, parse, error
import json
from datetime import datetime, timedelta

AUTH_URL = "https://api.fib.upc.edu/v2/o/authorize"
TOKEN_URL = "https://api.fib.upc.edu/v2/o/token"
JO_URL = "https://api.fib.upc.edu/v2/jo/"


def get_auth_url(client_id, host_uri, user_id):
    redirect_url = host_uri
    params = parse.urlencode({'redirect_uri': redirect_url, 'client_id': client_id,
                              'response_type': 'token', 'scope': 'read', 'state': user_id,
                              'approval_prompt': 'auto'}, doseq=True)
    return AUTH_URL + '?' + params


def get_access_token(access_token, token_type, expires_in, scope):
    expire_date = datetime.now() + timedelta(seconds=expires_in)
    return Token(access_token, token_type, expire_date, None, scope)

def get_name(token):
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + token.token,
        'User-agent': 'Mozilla/5.0'
    }
    req = request.Request(JO_URL, headers=headers, method='GET')
    try:
        with request.urlopen(req) as f:
            result = f.read()
        return User.from_json(result.decode('utf-8'))
    except error.HTTPError as e:
        print(e)
        print(e.read())
        raise RuntimeError()


def refresh_token(token, client_id, client_secret):
    if token.refresh_token == None:
        raise RuntimeError()
    data = parse.urlencode({'grant_type': 'refresh_token', 'refresh_token': token.token, 'client_id': client_id,
                            'client_secret': client_secret})
    with request.urlopen(TOKEN_URL, data) as f:
        result = f.read()
    return Token.from_json(result)


class Token:

    def __init__(self, token, type, expire_date, refresh_token, scope):
        self.token = token
        self.type = type
        self.expire_date = expire_date
        self.refresh_token = refresh_token
        self.scope = scope

    @classmethod
    def from_json(cls, data):
        j_data = json.loads(data)
        expire_data = datetime.today() + j_data['Expires_in']
        return Token(j_data['Access_token'], j_data['Token_type'], expire_data, j_data['Refresh_token'], j_data['Scope'])

class User:

    def __init__(self, name, surname, email, username, photo):
        self.name = name
        self.surname = surname
        self.email = email
        self.username = username
        self.photo = photo

    @classmethod
    def from_json(cls, data):
        j_data = json.loads(data)
        return User(j_data['nom'], j_data['cognoms'], j_data['email'], j_data['username'], j_data['foto'])
