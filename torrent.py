import sys
import requests
import os
import exception

#Global vars
pages = {
    'login' : 'https://ncore.pro/login.php',
    'list'  : 'https://ncore.pro/torrents.php'
}

login_credentials = {
    'username'  :   os.environ.get('NCORE_USER'),
    'pass'      :   os.environ.get('NCORE_PASS')
}

inputs = {
    'set_lang'  : 'hu',
    'submitted' : '1',
    'nev'       : login_credentials['username'],
    'pass'      : login_credentials['pass']
}


#Var check
for item in login_credentials.values():
    if item is None:
        raise exception.LoginCredentialsNotSet


#main
with requests.Session() as session:
    print('> Attempting to login to ncore.pro with credentials:', login_credentials)

    res = session.post(pages['login'], data = inputs)

    needle = 'Hibás felhasználónév' # This string is in response text if credentials are incorrect

    if needle in res.text:
        raise exception.InvalidUserOrPass
    else:
        print('> Login successfull')