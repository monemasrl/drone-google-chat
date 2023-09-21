import os
import requests
import json
import uuid
import hashlib
import datetime as dt

from pprint import pformat


def send_message(room_id, key, token, parameters=[]):
    threadKey = hashlib.md5(
        f"{parameters['REPO']}:{parameters['BRANCH']}".encode("utf-8")
    ).hexdigest()

    url = "https://chat.googleapis.com/v1/spaces/{}/messages?key={}&token={}&threadKey={}&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD".format(
        room_id, key, token, threadKey
    )
    headers = {"Content-Type": "application/json; charset=UTF-8"}

    buildWidgets = [
        {
            "decoratedText": {
                "topLabel": "Branch",
                "text": f"{parameters['BRANCH']}",
            }
        },
    ]

    formattedTime = dt.timedelta(
        seconds=int(parameters["STAGE_FINISHED"]) - int(parameters["STAGE_STARTED"])
    )

    buildWidgets.append(
        {
            "columns": {
                "columnItems": [
                    {
                        "widgets": [
                            {
                                "decoratedText": {
                                    "topLabel": "Status",
                                    "text": parameters["BUILD_STATUS"],
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "Author",
                                    "text": parameters["COMMIT_AUTHOR"],
                                }
                            },
                        ]
                    },
                    {
                        "widgets": [
                            {
                                "decoratedText": {
                                    "topLabel": "Duration",
                                    "text": f"{formattedTime}",
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "Commit",
                                    "text": f"<a href='{parameters['COMMIT_LINK']}'>{parameters['COMMIT_SHA'][:7]}</a>",
                                }
                            },
                        ]
                    },
                ]
            }
        }
    )

    sections = []
    buildSection = {
        "header": "Build Info",
        "collapsible": False,
        "widgets": buildWidgets,
    }
    sections.append(buildSection)
    repositorySection = {
        "header": "REPOSITORY",
        "collapsible": False,
        "widgets": [
            {
                "decoratedText": {
                    "text": f"{parameters['REPO']}",
                    "button": {
                        "text": "VIEW",
                        "onClick": {
                            "openLink": {
                                "url": f"{parameters['REPO_LINK']}",
                            }
                        },
                    },
                }
            },
        ],
    }
    sections.append(repositorySection)

    card = {
        "cardsV2": [
            {
                "cardId": uuid.uuid4().hex,
                "card": {
                    "header": {
                        "title": f"Build #<a href='{parameters['BUILD_LINK']}'>{parameters['BUILD_NUMBER']}</a> ({parameters['BRANCH']})",
                        "subtitle": f"{parameters['COMMIT_MESSAGE']}",
                        "imageUrl": "https://styles.redditmedia.com/t5_jt7nk/styles/communityIcon_62qfghr0oq931.png",
                        "imageType": "CIRCLE",
                        "imageAltText": "Drone CI",
                    },
                    "sections": sections,
                },
            }
        ],
    }

    response = requests.post(url, headers=headers, data=json.dumps(card))
    return response


if __name__ == "__main__":
    # Sostituisci con l'ID della tua chat room.
    room_id = os.environ.get("GOOGLE_CHAT_ID")
    google_key = os.environ.get("GOOGLE_KEY")
    google_token = os.environ.get("GOOGLE_TOKEN")
    variables = {}
    prefix: str = "DRONE_"
    for key, value in os.environ.items():
        if key[: len(prefix)] == prefix:
            variables[key[len(prefix) :]] = value

    if variables["BUILD_DEBUG"] == "true":
        for key, value in variables.items():
            print(f"{key}: {value}")
    # Invia il messaggio.
    response = send_message(room_id, google_key, google_token, parameters=variables)
