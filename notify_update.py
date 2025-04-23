#!/usr/bin/python3
# This script sends a notifications to Discord for each package that has been updated
# it reads the list of packages from ./packages/updated_packages.txt

import os, time
from datetime import datetime
import requests

# load discord URL from env secrets
try:
    discordurlEndpoint = os.environ['DISCORD_WEBHOOK_URL']
except KeyError:
    print("DISCORD_WEBHOOK_URL not set in environment variables")
    exit(1)

# based on the announcement method from appman
def announce_discord(package):
    current_time = int(time.time())
    path = "switch"
    color = "e60012"
    date = datetime.fromtimestamp(current_time).strftime('%d/%m/%Y %H:%M:%S')

    appurl = f"https://hb-app.store/{path}/{package}"
    icon = f"https://{path}.cdn.fortheusers.org/packages/{package}/icon.png"

    hook_object = {
        "username": "Switch Appstore Update",
        "avatar_url": "https://switch.cdn.fortheusers.org/packages/appstore/icon.png",
        "tts": False,
        "embeds": [
            {
                "title": "View Changelog",
                "type": "rich",
                "description": "",
                "url": appurl,
                "color": int(color, 16),
                "footer": {
                    "text": "fortheusers.org",
                    "icon_url": "https://wiiubru.com/images/switch_4tu_icon.png"
                },
                "thumbnail": {
                    "url": icon
                },
                "author": {
                    "name": f"App : {package}",
                    "url": appurl
                },
                "fields": [
                    {
                        "name": "Submitted : - ",
                        "value": date,
                        "inline": False
                    }
                ]
            }
        ]
    }

    response = requests.post(discordurlEndpoint, json=hook_object, headers={"Content-Type": "application/json"})
    return response.status_code

with open("packages/updated_packages.txt") as f:
    packages = f.read().split(",")
    for package in packages:
        package = package.strip()
        if package:
            status_code = announce_discord(package)
            if status_code == 204:
                print(f"Notification sent for {package}")
            else:
                print(f"Failed to send notification for {package}, status code: {status_code}")