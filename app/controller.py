import time
from quovo import Quovo, RequestError
from views import View


class Terminal:
    """The controller for the command line/terminal program. It utilizes the
    quovo.py module to interact with the Quovo API.
    """

    def __init__(self):
        self.quovo = Quovo()
        self.view = View()

    def parse_response(self, response):
        """Parses a response and its associated request into a dictionary.
        """
        return {
            'request': {
                'method': response.request.method,
                'url': response.request.url,
                'headers': response.request.headers,
                'body': response.request.body
            },
            # All responses from the Quovo API are returned as JSONs.
            'response': response.json()
        }

    def parse_and_print(self, response):
        """Pretty prints a response and its associated request.
        """
        parsed_response = self.parse_response(response)
        self.view.pretty_print_response(parsed_response)

    def parse_and_show_error(self, error):
        """Displays any response errors returned from the Quovo API.
        """
        msg = error.args[0]
        self.view.show_error(msg)
        response = error.args[1]
        return response

    def check_credentials(self):
        """Validates the given API user credentials.
        This is NOT a necessary step for API usage nor the typical Account
        creation process, rather it is simply an easy way to check if the
        given API user credentials are still valid.
        """
        username, password = self.view.get_credentials()
        try:
            response = self.quovo.check_credentials(username, password)
            self.view.confirm_credentials()
        except RequestError as e:
            response = self.parse_and_show_error(e)
            username, password = None, None
        finally:
            self.parse_and_print(response)
            self.view.next()
            return username, password

    def create_token(self, username, password):
        """Creates an Access Token using an inputted token name. This Access
        Token will be used to authenticate all future API requests.
        """
        token_name = self.view.get_token_name()
        try:
            response = self.quovo.create_token(username, password, token_name)
            token = response.json()['access_token']['token']
            # For ease, we will save the Access Token on the Quovo API instance,
            # so that all future API calls will be automatically authenticated
            # using the stored Access Token.
            self.quovo.set_token(token)
            self.view.confirm_token_creation()
        except RequestError as e:
            response = self.parse_and_show_error(e)
            token = None
        finally:
            self.parse_and_print(response)
            self.view.next()
            return token

    def create_user(self):
        """Creates a Quovo User with the given username.
        This User will then own any Accounts synced during the walkthrough.
        """
        # While other fields are usually nice to pass along in the
        # User creation request, like email or name, username is the only
        # required field.
        username = self.view.get_username()
        try:
            response = self.quovo.create_user(username)
            user_id = response.json()['user']['id']
            self.view.confirm_user_creation()
        except RequestError as e:
            response = self.parse_and_show_error(e)
            user_id = None
        finally:
            self.parse_and_print(response)
            self.view.next()
            # For ease, we will only return the id of the created User.
            # A typical create_user function will most likely return the entire
            # response body.
            return user_id

    def create_account(self, user_id):
        """Creates an Account using the inputted login credentials.
        """
        # These Account credentials are NOT the same as your API user
        # credentials. They are credentials for an account login within a
        # financial institution. For our test Brokerage, these
        # credentials do not matter.
        username, password = self.view.get_account_creds()
        try:
            # 21534 is the brokerage_id of our "Test Data Brokerage", which will
            # return an auto-generated sample Portfolio after a successful
            # Account sync.
            brokerage_id = 21534
            response = self.quovo.create_account(user_id, brokerage_id,
                                                 username, password)
            account_id = response.json()['account']['id']
            self.view.confirm_account_creation()
        except RequestError as e:
            response = self.parse_and_show_error(e)
            account_id = None
        finally:
            self.parse_and_print(response)
            self.view.next()
            # Again, we will only return the id of the created Account, instead
            # of the entire response body.
            return account_id

    def sync_account(self, account_id):
        """Initiates a sync on the given Account, which in our case, will be
        the Account we just created.
        """
        self.view.show_sync_info()
        try:
            response = self.quovo.sync_account(account_id)
            success = True
        except RequestError as e:
            response = self.parse_and_show_error(e)
            success = False
        finally:
            self.parse_and_print(response)
            return success

    def check_sync_status(self, account_id):
        """Checks the ongoing sync progress on the Account.
        This will continually check the Account's sync status, so we can
        receive sync progress in real-time.
        """
        def get_sync_status(account_id):
            response = self.quovo.get_sync_status(account_id)
            parsed_response = self.parse_response(response)
            return (response,
                    parsed_response['response']['sync']['progress'],
                    parsed_response['response']['sync']['status'])

        self.view.show_sync_status()
        try:
            response, progress, status = get_sync_status(account_id)
            # Continually fetch the sync status on the Account, so that we
            # can receive real-time updates on the sync progress.
            while status == "syncing":
                self.view.pretty_print_sync_status(progress)
                try:
                    time.sleep(0.5)
                    response, progress, status = get_sync_status(account_id)
                except RequestError as e:
                    response = self.parse_and_show_error(e)
                    time.sleep(3)
            # The Account status indicates the end result of the sync.
            # A "good" sync means the Account was synced successfully, without
            # any issues.
            self.view.show_account_status(status)
            if status == "good":
                self.parse_and_print(response)
                self.view.next()
            else:
                self.view.show_bad_sync()
            return status
        except RequestError as e:
            response = self.parse_and_show_error(e)
            self.parse_and_print(response)
            self.view.next()
            return None

    def get_account_portfolio(self, account_id):
        """Fetches the Portfolios within an Account.
        """
        try:
            response = self.quovo.get_account_portfolios(account_id)
            portfolios = response.json()['portfolios']
            # For ease, we are assuming this is a test Account with only a
            # single portfolio. Other Accounts may certainly have several
            # portfolios, but for demo purposes, we will ignore
            # those scenarios.
            portfolio_id = portfolios[0]['id']
            return portfolio_id
        except RequestError as e:
            response = self.parse_and_show_error(e)
            self.parse_and_print(response)
            return None

    def get_portfolio(self, portfolio_id):
        """Displays information about the given Portfolio.
        """
        self.view.show_portfolio()
        try:
            response = self.quovo.get_portfolio(portfolio_id)
        except RequestError as e:
            response = self.parse_and_show_error(e)
        finally:
            self.parse_and_print(response)
            self.view.back()

    def get_portfolio_positions(self, portfolio_id):
        """Displays the holdings or Position data in the given Portfolio.
        """
        self.view.show_positions()
        try:
            response = self.quovo.get_portfolio_positions(portfolio_id)
        except RequestError as e:
            response = self.parse_and_show_error(e)
        finally:
            self.parse_and_print(response)
            self.view.back()

    def get_portfolio_history(self, portfolio_id):
        """Displays the transaction History for the given Portfolio.
        """
        self.view.show_history()
        try:
            response = self.quovo.get_portfolio_history(portfolio_id)
        except RequestError as e:
            response = self.parse_and_show_error(e)
        finally:
            self.parse_and_print(response)
            self.view.back()

    def main(self):
        # This will continually attempt to check API user credentials until it
        # receives a valid username and password pair.
        username, password = self.check_credentials()
        while username is None or password is None:
            username, password = self.check_credentials()
        # Creates the API Access Token, which is used to authenticate all other
        # API requests.
        token = self.create_token(username, password)
        while token is None:
            token = self.create_token(username, password)
        # Creates a Quovo user
        user_id = self.create_user()
        while user_id is None:
            user_id = self.create_user()
        # Creates a new Account
        account_id = self.create_account(user_id)
        while account_id is None:
            account_id = self.create_account()
        # Initiates a sync on the Account
        sync_created = self.sync_account(account_id)
        # Check sync status will return "good" if the Account is synced
        # successfully with a final sync status of "good".
        if sync_created and self.check_sync_status(account_id) == "good":
            portfolio_id = self.get_account_portfolio(account_id)
            option = self.view.show_account_menu()
            while option != "4":
                if option == "1":
                    self.get_portfolio(portfolio_id)
                elif option == "2":
                    self.get_portfolio_positions(portfolio_id)
                elif option == "3":
                    self.get_portfolio_history(portfolio_id)
                option = self.view.show_account_menu()
            self.view.show_exit()
