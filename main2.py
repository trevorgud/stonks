from dotenv import load_dotenv
from schwab import auth, client
import json
import os


def main():
    load_dotenv()

    app_key = os.getenv('ACCESS_KEY')
    app_secret = os.getenv('SECRET_KEY')
    callback_url = 'https://127.0.0.1:8182/'
    token_path = './token.json'

    c = auth.easy_client(app_key, app_secret, callback_url, token_path)

    r = c.get_price_history_every_day('AAPL')
    r.raise_for_status()
    print(json.dumps(r.json(), indent=4))


if __name__ == "__main__":
    main()
