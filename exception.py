class LoginCredentialsNotSet(Exception):
    def __init__(self):
        print('Exception: One of the required environment variables is not set!')
        print('Use export command to set an env variable: export VARIABLE_NAME="VARIABLE_VALUE"')
        print('Variables need to be set: NCORE_USER, NCORE_PASS')


class InvalidUserOrPass(Exception):
    def __init__(self):
        print('Username or password is incorrect')