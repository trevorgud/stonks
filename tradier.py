from dotenv import load_dotenv
import json
import os
import requests


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


def buy_share(account_id, token, symbol):
    order_class = "equity"
    duration = "day"
    side = "buy"
    quantity = 1
    order_type = "limit"
    current_value = share_value(token, symbol)
    print(f"current value {current_value}")
    price = buying_limit(current_value)
    print(f"buying with limit {price}")
    # TODO: Implement the rest.


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


def main():
    load_dotenv()
    token = os.getenv('TRADIER_ACCESS_TOKEN')

    val = share_value(token, "AAPL")
    print(f"APPL={val}")

    buy_share(
        account_id="dummy/test",
        token=token,
        symbol="AAPL",
    )

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
