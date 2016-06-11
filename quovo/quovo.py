import json
import requests


class RequestError(Exception):
    """A catch-all exception for any non-good request.
    """

    def __init__(self, message, *args):
        self.message = message
        super(RequestError, self).__init__(message, *args)


class Quovo:
    """A partial wrapper for the Quovo API.
    This is not meant to be used as the basis for a production-ready API
    consumer, and is only for demonstrative purposes.
    """

    def __init__(self):
        # The base API URL
        self.root = 'https://api.quovo.com/v2'
        # The Access Token used to authenticate API requests
        self.token = None

    def check_response_status(self, response):
        """Checks for a non-good status code.
        """
        if response.status_code not in (200, 201, 204):
            # This simply raises an Exception that is caught and handled in
            # the controller. You might use more robust handlers for non-good
            # response statuses, depending on the error.
            message = response.json()['message']
            raise RequestError(message, response)

    def make_request(self, method, path, params=None, headers=None,
                     auth=None, token_auth=True):
        """A simple helper method/wrapper around all HTTP requests.
        """
        headers = headers or {}
        # To authenticate an API request, pass the appropriate Access Token in
        # the request header. This follows typical Bearer Token Authorization.
        if token_auth and self.token:
            headers['Authorization'] = 'Bearer {0}'.format(self.token)
        if method == "GET":
            response = requests.get(self.root + path,
                                    auth=auth,
                                    headers=headers,
                                    params=params)
        elif method == "POST":
            headers['Content-Type'] = 'application/json'
            data = json.dumps(params or {})
            response = requests.post(self.root + path,
                                     auth=auth,
                                     headers=headers,
                                     data=data)
        self.check_response_status(response)
        # For illustrative purposes, we are returning the entire response
        # object, instead of just the response content or body.
        return response

    def check_credentials(self, username, password):
        """Authenticates API user credentials. If the credentials are valid,
        the request will return all available authentication tokens.
        """
        # Authentication on the /tokens endpoint uses Basic Authorization
        # to verify your API user credentials.
        return self.make_request('GET', '/tokens',
                                 auth=(username, password),
                                 token_auth=False)

    def create_token(self, username, password, name):
        """Creates a new API Access Token.
        """
        params = {'name': name}
        return self.make_request('POST', '/tokens',
                                 params=params,
                                 auth=(username, password),
                                 token_auth=False)

    def set_token(self, token):
        """Saves the token instance, so all future API requests can implicitly
        authenticate themselves inside make_request.
        """
        self.token = token

    def create_user(self, username):
        """Creates a Quovo User.
        """
        params = {'username': username}
        return self.make_request('POST', '/users', params=params)

    def create_account(self, user_id, brokerage_id, username, password):
        """Creates a new Account on the given User.
        """
        # The username and password used here are NOT the same as your API
        # User credentials. They are specific to an account login at a
        # financial institution.
        params = {
            'brokerage': brokerage_id,
            'username': username,
            'password': password
        }
        return self.make_request('POST', '/users/{0}/accounts'.format(user_id),
                                 params=params)

    def get_sync_status(self, account_id):
        """Gets the current sync status on an Account.
        """
        return self.make_request('GET', '/accounts/{0}/sync'.format(account_id))

    def sync_account(self, account_id):
        """Initiates a sync on the given Account.
        """
        return self.make_request('POST', '/accounts/{0}/sync'.format(account_id))

    def get_account_portfolios(self, account_id):
        """Fetches all of an Account's Portfolios.
        """
        return self.make_request('GET', '/accounts/{0}/portfolios'.format(account_id))

    def get_portfolio(self, portfolio_id):
        """Fetches information on a single Portfolio.
        """
        return self.make_request('GET', '/portfolios/{0}'.format(portfolio_id))

    def get_portfolio_positions(self, portfolio_id):
        """Fetches a Portfolio's holdings or Position data.
        """
        return self.make_request('GET', '/portfolios/{0}/positions'.format(portfolio_id))

    def get_portfolio_history(self, portfolio_id):
        """Fetches a Portfolio's available transaction History.
        """
        return self.make_request('GET', '/portfolios/{0}/history'.format(portfolio_id))
