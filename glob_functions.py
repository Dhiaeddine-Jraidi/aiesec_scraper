import requests

BOT_TOKEN_key = "7099537302:AAEg_9hW3k6u1qKTwpH28McZD546xIWa9ik"


def send_message(message):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN_key}/sendMessage", data={'chat_id': '1545111998','text': message})