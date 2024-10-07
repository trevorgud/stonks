from dotenv import load_dotenv
from schwab import auth, client
import schwabdev

import argparse
import json
import os

## Goals

## Buy 1 of each stock per account
## Don't buy 1 if already owned 1
## Don't buy 1 if order already submitted for 1
## Post a warning if attempting to buy a stock above a certain limit (greater $1)
## Handle errors: terminate if any error, can try again later or adjust params for new trades.

## Sell 1 of each per account
## Don't sell 1 if not owned 1
## Post a warning if stock below certain limit (less $1)
## Handle errors: terminate if any error.


from typing import Optional


def design_order(
    symbol,
    order_type,
    instruction,
    quantity,
    leg_id,
    order_leg_type,
    asset_type,
    price: Optional[str] = None,
    session="NORMAL",
    duration="DAY",
    complex_order_strategy_type="NONE",
    tax_lot_method="FIFO",
    position_effect="OPENING",
    # special_instruction="ALL_OR_NONE",
    order_strategy_type="SINGLE",
):

    post_order_payload = {
        "price": price,
        "session": session,
        "duration": duration,
        "orderType": order_type,
        "complexOrderStrategyType": complex_order_strategy_type,
        "quantity": quantity,
        "taxLotMethod": tax_lot_method,
        "orderLegCollection": [
            {
                "orderLegType": order_leg_type,
                "legId": leg_id,
                "instrument": {
                    "symbol": symbol,
                    "assetType": asset_type,
                },
                "instruction": instruction,
                "positionEffect": position_effect,
                "quantity": quantity,
            }
        ],
        "orderStrategyType": order_strategy_type,
    }

    return post_order_payload


class InProgress():
    def __init__(self, acctPositions, orders):
        self.positions = {}
        for account in acctPositions:
            positions = account['securitiesAccount']['positions']
            # TODO: Implement storage of account positions and open orders to track which trades are
            # already in progress.
        self.orders = orders
    
    def isInProgress(account, symbol):
        # TODO: Implement
        return False


def buy(accountHash, symbol):
    post_order_payload = design_order(
                symbol,
                # price="5000",
                order_type="MARKET",
                instruction="BUY",
                quantity=f"1",
                leg_id="1",
                order_leg_type="EQUITY",
                asset_type="EQUITY",
            )
    print(json.dumps(post_order_payload))
    resp = client.order_place(accountHash=accountHash, order=post_order_payload)
    code = resp.status_code
    print(code)
    body = json.dumps(resp.json())
    print(body)
    return resp


def main():
    load_dotenv()

    app_key = os.getenv('CHARLES_ACCESS_KEY')
    app_secret = os.getenv('CHARLES_SECRET_KEY')
    callback_url = 'https://127.0.0.1:8182/'
    token_path = './token.json'

    ## Schwabdev
    client = schwabdev.Client(app_key, app_secret)
    accounts = client.account_linked().json()
    print(accounts)

    details = client.account_details_all(fields='positions').json()
    json_string = json.dumps(details)
    # print(json_string)

    # Create the parser object
    parser = argparse.ArgumentParser(description="Process stock transactions: buy or sell a stock")

    # Add mutually exclusive group for --buy and --sell
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--buy', action='store_true', help='Buy a stock')
    group.add_argument('--sell', action='store_true', help='Sell a stock')

    # Add the stock symbol argument
    parser.add_argument('symbol', type=str, help='The stock symbol to buy or sell')

    # Parse the arguments
    args = parser.parse_args()

    # Handle buy or sell action
    if args.buy:
        print(f"Buying stock: {args.symbol}")
    elif args.sell:
        print(f"Selling stock: {args.symbol}")

    for account in accounts:
        account_num = account['accountNumber']
        hash_val = account['hashValue']
        post_order_payload = design_order(
                    args.symbol,
                    # price="5000",
                    order_type="MARKET",
                    instruction="BUY",
                    quantity=f"1",
                    leg_id="1",
                    order_leg_type="EQUITY",
                    asset_type="EQUITY",
                )
        print(json.dumps(post_order_payload))
        resp = client.order_place(accountHash=hash_val, order=post_order_payload)
        code = resp.status_code
        print(code)
        body = json.dumps(resp.json())
        print(body)

        # # TODO: Use this one instead, not inline:
        # buy(accountHash=hash_val, symbol=args.symbol)

        # if code >= 300:
        #     print(body)
        break


    ## Schwab-py
    # c = auth.easy_client(app_key, app_secret, callback_url, token_path, interactive=False)
    # r = c.get_price_history_every_day('AAPL')
    # r.raise_for_status()
    # print(json.dumps(r.json(), indent=4))


if __name__ == "__main__":
    main()




        # # From charles schwab developer api docs:
        # order = {
        #     "session": "NORMAL",
        #     "duration": "DAY",
        #     "orderType": "MARKET",
        #     # "cancelTime": "2024-10-07T17:42:29.985Z",
        #     "complexOrderStrategyType": "NONE",
        #     "quantity": 1,
        #     # "filledQuantity": 0,
        #     # "remainingQuantity": 0,
        #     "orderLegCollection": [
        #         {
        #         "orderLegType": "EQUITY",
        #         "legId": 1,
        #         "instrument": {
        #             # "cusip": "string",
        #             "symbol": args.symbol,
        #             # "description": "string",
        #             # "instrumentId": 0,
        #             # "netChange": 0,
        #             # "type": "SWEEP_VEHICLE"
        #         },
        #         "instruction": "BUY",
        #         "positionEffect": "OPENING",
        #         "quantity": 1,
        #         # "quantityType": "ALL_SHARES",
        #         # "divCapGains": "REINVEST",
        #         # "toSymbol": "string"
        #         }
        #     ],
        #     # "destinationLinkName": "string",
        #     # "releaseTime": "2024-10-07T17:42:29.985Z",
        #     # "stopPrice": 0,
        #     # "stopPriceLinkBasis": "MANUAL",
        #     # "stopPriceLinkType": "VALUE",
        #     # "stopPriceOffset": 0,
        #     # "stopType": "STANDARD",
        #     # "priceLinkBasis": "MANUAL",
        #     # "priceLinkType": "VALUE",
        #     # "price": 0,
        #     "taxLotMethod": "FIFO",
        #     # "activationPrice": 0,
        #     # "specialInstruction": "ALL_OR_NONE",
        #     "orderStrategyType": "SINGLE",
        #     # "orderId": 0,
        #     # "cancelable": false,
        #     # "editable": false,
        #     # "status": "AWAITING_PARENT_ORDER",
        #     # "enteredTime": "2024-10-07T17:42:29.985Z",
        #     # "closeTime": "2024-10-07T17:42:29.985Z",
        #     "accountNumber": account_num,
        #     # "orderActivityCollection": [
        #     #     {
        #     #     "activityType": "EXECUTION",
        #     #     "executionType": "FILL",
        #     #     "quantity": 0,
        #     #     "orderRemainingQuantity": 0,
        #     #     "executionLegs": [
        #     #         {
        #     #         "legId": 0,
        #     #         "price": 0,
        #     #         "quantity": 0,
        #     #         "mismarkedQuantity": 0,
        #     #         "instrumentId": 0,
        #     #         "time": "2024-10-07T17:42:29.985Z"
        #     #         }
        #     #     ]
        #     #     }
        #     # ],
        #     # "replacingOrderCollection": [
        #     #     "string"
        #     # ],
        #     # "childOrderStrategies": [
        #     #     "string"
        #     # ],
        #     # "statusDescription": "string"
        # }