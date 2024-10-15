from dotenv import load_dotenv
import json
import os
import requests
import argparse


# If data is a list, return that list.
# If data is a single object (dict), wrap it in a list and return.
def validate_list(data):
    if isinstance(data, dict):
        return [data]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Expected a dictionary or list of dictionaries.")


BUY_LIMIT_MULTIPLIER = 1.1
SELL_LIMIT_MULTIPLIER = 0.9

def buying_limit(current_val):
    limit = current_val * BUY_LIMIT_MULTIPLIER
    limit = round(limit, 2)
    return limit

def selling_limit(current_val):
    limit = current_val * SELL_LIMIT_MULTIPLIER
    limit = round(limit, 2)
    return limit


def handle_account(account_id, token):
    balance_url = f"https://api.tradier.com/v1/accounts/{account_id}/balances"
    # Headers, including the Authorization Bearer Token and Accept header
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    # Make the GET request
    response = requests.get(balance_url, headers=headers)
    data = response.json()
    print(f"account={account_id}", data)


def place_order(account_id, token, symbol, side, quantity):
    orders_url = f"https://api.tradier.com/v1/accounts/{account_id}/orders"
    # Headers, including the Authorization Bearer Token and Accept header
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    # class - The kind of order to be placed. One of: equity, option, multileg, combo.
    # symbol - The symbol to be ordered.
    # duration - The time for which the order will be remain in effect (Day or GTC).
    # side - The side of the order (buy or sell).
    # quantity - The number of shares to be ordered, in whole numbers.
    # type - The type of order to be placed (market, limit, etc.)
    ##
    # POST /v1/accounts/12345678/orders HTTP/1.1
    # Host: api.tradier.com
    # Accept: \*/\*
    # class=equity&symbol=AAPL&duration=day&side=buy&quantity=100&type=market
    params = {
        "class": "equity",
        "symbol": symbol,
        "duration": "day",
        "side": side,
        "quantity": quantity,
        "type": "market",
    }
    print(account_id, params)
    # Make the GET request
    response = requests.post(orders_url, headers=headers, params=params)
    print(response.status_code)
    print(response.text)
    return response


def share_value(token, symbol):
    # API allows comma separated symbols, can consider supporting this later but no current support.
    if "," in symbol:
        print("Multi share value not supported, returning single symbol value")

    quotes_url = f"https://api.tradier.com/v1/markets/quotes"

    # Headers, including the Authorization Bearer Token and Accept header
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    params = {
        "symbols": [symbol],
    }

    # Make the GET request
    response = requests.get(quotes_url, headers=headers, params=params)
    data = response.json()
    quotes = data["quotes"]["quote"]
    quotes = validate_list(quotes)
    if len(quotes) < 0:
        raise Exception("No quotes found")
    # Only returning the first quote value found.
    quote = quotes[0]
    value = quote["last"]
    return value


def account_ids(token):
    profile = user_profile(token)
    accounts = profile['profile']['account']
    account_ids = []
    for account in accounts:
        account_number = account['account_number']
        print(account_number)
        account_ids.append(account_number)
    return account_ids


def user_profile(token):
    profile_url = f"https://api.tradier.com/v1/user/profile"
    # Headers, including the Authorization Bearer Token and Accept header
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    # Make the GET request
    response = requests.get(profile_url, headers=headers)
    data = response.json()
    print(data)
    return data


def account_symbols(account_id, token):
    symbols = []
    positions = account_positions(account_id, token)
    if positions['positions'] == 'null':
        return symbols
    found_positions = positions['positions']['position']
    for each in found_positions:
        symbols.append(each['symbol'])
    return symbols


def account_positions(account_id, token):
    positions_url = f"https://api.tradier.com/v1/accounts/{account_id}/positions"
    # Headers, including the Authorization Bearer Token and Accept header
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    # Make the GET request
    response = requests.get(positions_url, headers=headers)
    data = response.json()
    print(data)
    return data


class InProgress():
    def __init__(self):
        self.positions = {}

    def addSymbols(self, account_id, symbols):
        self.positions[account_id] = symbols

    def isInProgress(self, account_id, symbol):
        # TODO: Implement
        accountSymbols = self.positions[account_id]
        return symbol in accountSymbols


def get_all_progress(token):
    progress = InProgress()
    ids = account_ids(token=token)
    for id in ids:
        symbols = account_symbols(account_id=id, token=token)
        progress.addSymbols(id, symbols)
    return progress


def main():
    load_dotenv()
    token = os.getenv('TRADIER_ACCESS_TOKEN')

    # Create the parser object
    parser = argparse.ArgumentParser(description="Process stock transactions: buy or sell a stock")

    # Add mutually exclusive group for --buy and --sell
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--buy', action='store_true', help='Buy a stock')
    group.add_argument('--sell', action='store_true', help='Sell a stock')

    # Add the stock symbol argument
    parser.add_argument('symbol', type=str, help='The stock symbol to buy or sell')

    parser.add_argument(
        '--quantity',
        type=int,
        default=1,
        help='Stock quantity',
    )

    # Parse the arguments
    args = parser.parse_args()

    # Handle buy or sell action
    if args.buy:
        print(f"Buying stock: {args.symbol}")
    elif args.sell:
        print(f"Selling stock: {args.symbol}")

    progress = get_all_progress(token)

    ids = account_ids(token=token)
    for id in ids:
        stockInProgress = progress.isInProgress(id, args.symbol)
        if args.buy and not stockInProgress:
            resp = place_order(
                account_id=id,
                token=token,
                symbol=args.symbol,
                side="buy",
                quantity=1,
            )
            if resp.status_code >= 300:
                break
        elif args.sell and stockInProgress:
            resp = place_order(
                account_id=id,
                token=token,
                symbol=args.symbol,
                side="sell",
                quantity=1,
            )
            if resp.status_code >= 300:
                break


    # val = share_value(token, "AAPL")
    # print(f"APPL={val}")

    # buy_share(
    #     account_id="dummy/test",
    #     token=token,
    #     symbol="AAPL",
    # )

    # # URL for the GET request
    # url = "https://api.tradier.com/v1/user/profile"

    # # Headers, including the Authorization Bearer Token and Accept header
    # headers = {
    #     'Authorization': f'Bearer {token}',
    #     'Accept': 'application/json'
    # }

    # # Make the GET request
    # response = requests.get(url, headers=headers)

    # # Check if the request was successful
    # if response.status_code == 200:
    #     # Parse the JSON response
    #     data = response.json()
    #     print(data)
    #     accounts = data["profile"]["account"]
    #     accounts = validate_list(accounts)
    #     if len(accounts) < 0:
    #         raise Exception("No accounts found")
    #     account = accounts[0]
    #     print(account["account_number"])
    #     for account in accounts:
    #         handle_account(account["account_number"], token)

    # else:
    #     # Print error details
    #     print(f"Error: {response.status_code}, {response.text}")


if __name__ == "__main__":
    main()
