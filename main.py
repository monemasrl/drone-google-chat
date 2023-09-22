import os
import requests
import json
import uuid
import hashlib
import datetime as dt

from pprint import pformat


def send_message(room_id, key, token, use_thread, parameters=[]):
    threadKey = hashlib.md5(
        f"{parameters['REPO']}:{parameters['BRANCH']}".encode("utf-8")
    ).hexdigest()

    if use_thread == "true":
        thread_option = "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"
    else:
        thread_option = "MESSAGE_REPLY_OPTION_UNSPECIFIED"
    url = "https://chat.googleapis.com/v1/spaces/{}/messages?key={}&token={}&threadKey={}&messageReplyOption={}".format(
        room_id, key, token, threadKey, thread_option
    )
    headers = {"Content-Type": "application/json; charset=UTF-8"}

    buildWidgets = []

    if "FAILED_STAGES" in parameters:
        failedStages = parameters["FAILED_STAGES"]
        buildWidgets.append(
            {
                "decoratedText": {
                    "topLabel": "Failed Stages",
                    "text": f"{failedStages}",
                }
            }
        )

    buildWidgets.append(
        {
            "decoratedText": {
                "topLabel": "Trigger event",
                "text": f"{parameters['BUILD_EVENT'].upper()}",
            }
        },
    )

    formattedTime = dt.timedelta(
        seconds=int(parameters["BUILD_FINISHED"]) - int(parameters["BUILD_CREATED"])
    )

    if parameters["BUILD_STATUS"] == "success":
        status = "<span style='background-color: #green'><font color=\"#00ff00\">SUCCESS</font></span>"
        color = {"red": 0, "green": 1, "blue": 0, "alpha": 1}
    else:
        status = '<font color="#ff0000">FAILED</font>'
        color = {"red": 1, "green": 0, "blue": 0, "alpha": 1}

    buildWidgets.append(
        {
            "columns": {
                "columnItems": [
                    {
                        "widgets": [
                            {
                                "decoratedText": {
                                    "topLabel": "Status",
                                    "button": {
                                        "text": status,
                                        "color": color,
                                        "onClick": {
                                            "openLink": {
                                                "url": f"{parameters['BUILD_LINK']}",
                                            }
                                        },
                                    },
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
    if "DEPLOY_TO" in parameters:
        header = "Deployment Info"
    else:
        header = "Build Info"

    buildSection = {
        "header": header,
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

    if "DEPLOY_TO" in parameters:
        title = f"Deployed {parameters['REPO_NAME']}#<a href='{parameters['BUILD_LINK']}'>{parameters['BUILD_PARENT']}</a> to {parameters['DEPLOY_TO'].upper()}"
        subtitle = f"Triggered by {parameters['BUILD_TRIGGER']}"
    else:
        title = f"Build #<a href='{parameters['BUILD_LINK']}'>{parameters['BUILD_NUMBER']}</a> ({parameters['BRANCH']})"
        subtitle = f"{parameters['COMMIT_MESSAGE']}"

    card = {
        "cardsV2": [
            {
                "cardId": uuid.uuid4().hex,
                "card": {
                    "header": {
                        "title": title,
                        "subtitle": subtitle,
                        "imageUrl": "https://styles.redditmedia.com/t5_jt7nk/styles/communityIcon_62qfghr0oq931.png",
                        "imageType": "CIRCLE",
                        "imageAltText": "Drone CI",
                    },
                    "sections": sections,
                },
            }
        ],
    }

    if parameters["BUILD_DEBUG"] == "true":
        print(f"Sending message to {room_id}")
        print(f"Message: {pformat(card)}")
    response = requests.post(url, headers=headers, data=json.dumps(card))
    return response


if __name__ == "__main__":
    # Sostituisci con l'ID della tua chat room.
    room_id = os.environ.get("GOOGLE_CHAT_ID")
    google_key = os.environ.get("GOOGLE_KEY")
    google_token = os.environ.get("GOOGLE_TOKEN")
    google_thread = os.environ.get("GOOGLE_THREAD", default="false")
    variables = {}
    prefix: str = "DRONE_"
    for key, value in os.environ.items():
        if key[: len(prefix)] == prefix:
            variables[key[len(prefix) :]] = value

    if variables["BUILD_DEBUG"] == "true":
        for key, value in variables.items():
            print(f"{key}: {value}")
    # Invia il messaggio.
    response = send_message(
        room_id, google_key, google_token, google_thread, parameters=variables
    )

    if variables["BUILD_DEBUG"] == "true":
        print(f"Status code: {response.status_code}")
        print(f"Response: {pformat(response.json())}")
