import os
import requests
import json

from pprint import pformat


# https://chat.googleapis.com/v1/spaces/AAAA5Y3zyRw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=EcQCJrOi_CImQZFWNqBRplNjtlZPxQMYf87R861nVX0
def send_message(room_id, key, token, message, parameters=[]):
    """
    Invia un messaggio ad una chat room Google attraverso webhook.

    Args:
      room_id: L'ID della chat room.
      key: La chiave di accesso.
      token: Il token di accesso.
      message: Il messaggio da inviare.

    Returns:
      Il codice di risposta HTTP.
    """

    url = "https://chat.googleapis.com/v1/spaces/{}/messages?key={}&token={}".format(
        room_id, key, token
    )
    url = "https://chat.googleapis.com/v1/spaces/AAAA5Y3zyRw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=EcQCJrOi_CImQZFWNqBRplNjtlZPxQMYf87R861nVX0"
    headers = {"Content-Type": "application/json; charset=UTF-8"}

    widgets = [
        {
            "decoratedText": {
                "startIcon": {
                    "iconUrl": "https://raster.shields.io/badge/Build-Success-green",
                },
                "text": "Build Status",
            }
        }
    ]
    for key, value in parameters.items():
        widgets.append({"textParagraph": {"text": f"{key}: {value}"}})

    card = {
        "cardsV2": [
            {
                "cardId": "unique-card-id",
                "card": {
                    "header": {
                        "title": f"Build #{parameters['BUILD_NUMBER']}",
                        "subtitle": f"{parameters['BUILD_COMMIT_MESSAGE']}",
                        "imageUrl": "https://styles.redditmedia.com/t5_jt7nk/styles/communityIcon_62qfghr0oq931.png",
                        "imageType": "CIRCLE",
                        "imageAltText": "Drone CI",
                    },
                    "sections": [
                        {
                            "header": "Build Info",
                            "collapsible": True,
                            "uncollapsibleWidgetsCount": 1,
                            "widgets": widgets,
                        },
                    ],
                },
            }
        ],
    }

    print(pformat(card))
    data = {"text": message}

    response = requests.post(url, headers=headers, data=json.dumps(card))
    return response.json()


if __name__ == "__main__":
    # Sostituisci con l'ID della tua chat room.
    room_id = os.environ.get("GOOGLE_CHAT_ID")
    key = os.environ.get("GOOGLE_KEY")
    token = os.environ.get("GOOGLE_TOKEN")
    variables = {}
    prefix: str = "DRONE_"
    for key, value in os.environ.items():
        if key[: len(prefix)] == prefix:
            variables[key[len(prefix) :]] = value

    print(pformat(variables))
    # Sostituisci con il messaggio che vuoi inviare.
    message = "Ciao mondo!"

    # Invia il messaggio.
    response = send_message(room_id, key, token, message, parameters=variables)

    # Stampa il codice di risposta HTTP.
    print(pformat(response))
