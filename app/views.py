import getpass
import json
import os


class View:
    """The views (i.e. print statements) for the command line/terminal program.
    """

    def __init__(self):
        self.delimiter = "-" * 60

    def clear(self):
        """Clears out any text currently displayed on the terminal window.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def pretty_print_response(self, response):
        def pretty_print_json(data):
            return json.dumps(data, indent=4, sort_keys=True)

        request = response['request']
        print self.delimiter
        print """Request:
{0} {1}

Request Headers:
{2}

Request Params:
{3}

Response:
{4}
""".format(request['method'],
           request['url'],
           "Authorization: {0}".format(request['headers']['Authorization']),
           pretty_print_json(json.loads(request['body'])) if request['body'] else '',
           pretty_print_json(response['response']))

    def show_error(self, error):
        print "\nAPI Request Error: {0}".format(error)

    def next(self):
        raw_input("\nPress enter to continue...")

    def back(self):
        raw_input("\nPress enter to go back to the Account menu.")

    def get_credentials(self):
        self.clear()
        print """Welcome to Quovo's interactive API tutorial! This Python program will connect directly to the Quovo API, and walk through how to:

- Create an API Access Token with your Quovo API credentials.
- Create a Quovo User.
- Create and sync an Account on one of our available Test Brokerages.
- Retrieve Portfolios associated with this newly created Account.
- Retrieve Positions and History for these Portfolios.


Let's begin by validating your API user credentials.
"""
        username = raw_input("Username: ")
        password = getpass.getpass("Password: ")
        return username, password

    def confirm_credentials(self):
        print "\nYour API user credentials look good.\n"

    def get_token_name(self):
        self.clear()
        print """Next, we will need to create an API Access Token.

This Access Token will be used to authenticate our API user during all subsequent
API requests.
"""
        token_name = raw_input("Let's name this new Token: ")
        return token_name

    def confirm_token_creation(self):
        print """\nGreat, we have successfully created a new Access Token.
We can now authenticate ourselves properly when making future API requests.
"""

    def get_username(self):
        self.clear()
        print """Now that we have our Token, let's actually do something with it.

First, we are going to make a Quovo User. This User will be the owner of any
Accounts we create.

All Quovo Users also require a username. This username will usually be related
to a username within your internal system.
"""
        username = raw_input("Enter the new User's username: ")
        return username

    def confirm_user_creation(self):
        print """\nNice, we now have a new Quovo User we can sync Accounts to.\n"""

    def get_account_creds(self):
        self.clear()
        print """Next, we are going to create an Account for the new User.

A Quovo Account is equivalent to a login at a financial institution. For this
demo, we will create an Account on a Quovo Test Brokerage instead of a
live institution.

Enter the credentials for the new Account (for this particular Test Brokerage,
the username and password do not matter).
"""
        username = raw_input("Username: ")
        password = raw_input("Password: ")
        return username, password

    def confirm_account_creation(self):
        print "\nThe account was added succesfully!\n"

    def show_sync_info(self):
        self.clear()
        print """Now, we will intitiate a sync on the Account we just created.

Syncs represent ongoing updates on a given Account. After creating an Account,
you will always need to trigger a sync to actually update it and begin fetching
the relevant financial data.
"""
        self.next()

    def show_sync_status(self):
        print self.delimiter
        print """We have successfully initiated a sync on the Account.

Let's check the ongoing sync progress...
"""

    def pretty_print_sync_status(self, sync):
        print "Message: {0} Sync progress: {1:.0f}%".format(
            sync['message'].ljust(25),
            sync['percent'] * 100
        )

    def show_account_status(self, status):
        print """\nAll done!

The final sync status on the Account: {0}""".format(status)
        print self.delimiter

    def show_bad_sync(self, status):
        print "Oops, looks like there was an issue while syncing the account."

    def show_account_menu(self):
        self.clear()
        print """Now that we have synced our Account, we can finally check out
its financial data.

Enter one of the following options to view the relevant data on the Account:

1 - Portfolio
2 - Positions
3 - History
4 - Exit
"""
        user_input = raw_input("Select an option: ")
        return user_input

    def show_portfolio(self):
        self.clear()
        print """Here is the Account's Portfolio.

A Portfolio represents subaccounts found within a financial institution login.
Positions and History actually belong to a single Portfolio, NOT an Account.
"""

    def show_positions(self):
        self.clear()
        print "Here are the Positions or holdings within the Account's Portfolio.\n"

    def show_history(self):
        self.clear()
        print "Here are the historical transactions within the Account's Portfolio.\n"

    def show_exit(self):
        print "\nGoodbye.\n"
