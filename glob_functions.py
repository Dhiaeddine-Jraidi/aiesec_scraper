import requests
import os
import requests, msal
from datetime import datetime, timedelta


client_id="c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12"
BOT_TOKEN_key = "7099537302:AAEg_9hW3k6u1qKTwpH28McZD546xIWa9ik"
dataset_id = "a19b3981-a2d7-43d7-8444-26960029bd8c"
url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
refresh_token_file = 'files/refresh_token.pem'
scopes = ["https://analysis.windows.net/powerbi/api/.default"]
authority = "https://login.microsoftonline.com/organizations"
username = "dhiaeddine.jraidi@tbs.u-tunis.tn"
password = "Dhia@548234"


def send_message(message):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN_key}/sendMessage", data={'chat_id': '1545111998','text': message})


def cleaning(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


def get_access_token():
    app = msal.PublicClientApplication(client_id=client_id, authority=authority)
    try:
        with open(refresh_token_file, 'r') as file:
            refresh_token = file.read()
        
        result = app.acquire_token_by_refresh_token(refresh_token, scopes)
        with open(refresh_token_file, 'w') as file:
            file.write(result['refresh_token'])
        return result['access_token']
       
    except Exception as e:
        print(e)
        try:
            result = app.acquire_token_by_username_password(username, password, scopes=scopes)
            with open(refresh_token_file, 'w') as file:
                file.write(result['refresh_token'])
            return result['access_token']
        except Exception as e:
             print(e)
             return None
             



def powerbi_get_refresh_date():
        access_token = get_access_token()
        params = {"top": 1}
        headers = {
        "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
                data = response.json()
                completed_refreshes = [item for item in data['value'] if item['status'] == 'Completed']
                if completed_refreshes:
                        last_refresh = max(completed_refreshes, key=lambda x: x['endTime'])
                        last_refresh_datetime = datetime.strptime(last_refresh['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        updated_datetime = last_refresh_datetime + timedelta(hours=1)
                        formatted_datetime = updated_datetime.strftime("%m-%d-%Y @ %I %p").lstrip("0")
                        return formatted_datetime
                else:
                        return "n/a" 
        else:
                return "n/a"



def powerbi_refresh_dataset():
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 202:
        return 1
    else:
        return 0
    

        
