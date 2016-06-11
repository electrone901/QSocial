from quovo import Quovo
import sys, time

from controller import Terminal

quser = "alvikabir@nyu.edu"
qpass = "laurenisthebest"

token = sys.argv[1]
print "---Token: " + token

quovo = Quovo()

quovo.set_token(token)

def parse_response(response):
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

def create_user(username):
    response = quovo.create_user(username)
    user_id = response.json()['user']['id']
    print "Username: " + username + " Id: "  + str(user_id)
    return user_id

def create_account(userid):
    username = "testUsername"
    password = "testPassword"
    brokers = [6]
    bk_id = 21534
    response = quovo.create_account(userid, bk_id, username, password)
    account_id = response.json()['account']['id']
    print "UserId: " + str(userid) + " AccId: " + str(account_id)
    return account_id

def get_account_portfolio(account_id):
    response = quovo.get_account_portfolios(account_id)
    portfolios = response.json()['portfolios']
    portfolio_id = portfolios[0]['id']
    print "acccount id: " + str(account_id) + " portfolio_id:  " + str(portfolio_id)
    return portfolio_id

def sync_account(account_id):
    response = quovo.sync_account(account_id)
    print "Syncing... " + str(account_id)
    print parse_response(response)

def check_sync_status(account_id):
    """Checks the ongoing sync progress on the Account.
    This will continually check the Account's sync status, so we can
    receive sync progress in real-time.
    """
    def get_sync_status(account_id):
        response = quovo.get_sync_status(account_id)
        parsed_response = parse_response(response)
        return (response,
                parsed_response['response']['sync']['progress'],
                parsed_response['response']['sync']['status'])

    try:
        response, progress, status = get_sync_status(account_id)
        # Continually fetch the sync status on the Account, so that we
        # can receive real-time updates on the sync progress.
        while status == "syncing":
            try:
                time.sleep(0.5)
                response, progress, status = get_sync_status(account_id)
            except Exception as e:
                print "error while syncing"
                time.sleep(3)
        # The Account status indicates the end result of the sync.
        # A "good" sync means the Account was synced successfully, without
        # any issues.
        if status == "good":
            print "good sync"
        else:
            print "bad sync"
        return status
    except Exception as e:
        print "sync status error" + str(e)

def get_portfolio(portfolio_id):
    response = quovo.get_portfolio_positions(portfolio_id)
    return response

def get_eq_portfolio(portfolio_id):
    response  = get_portfolio(portfolio_id)
    positions = response.json()['positions']
    portfolio = {'eq_pos':[]}
    if len(positions) > 0:
        portfolio['id'] = positions[0]['account']
        portfolio['name'] = positions[0]['portfolio_name']
    for position in positions:
        if position['security_type'] == 'Equity':
            portfolio['eq_pos'].append(extract(position))
    print portfolio
    return portfolio

def extract(data):
    base = {'sym': data['ticker'], 'qty': data['quantity'], 'price': data['price']}
    return base

def get_portfolio_history(portfolio_id):
    response = quovo.get_portfolio_history(portfolio_id)
    print parse_response(response)

userid1 = create_user("alchen1")
accid1 = create_account(userid1)
sync_account(accid1)
check_sync_status(accid1)
#accid1 = 974190
portid1 = get_account_portfolio(accid1)
#get_portfolio(portid1)
eq_port = get_eq_portfolio(portid1)
print eq_port
#get_portfolio_history(portid1)

#t = Terminal()
#t.create_token(quser, qpass)
