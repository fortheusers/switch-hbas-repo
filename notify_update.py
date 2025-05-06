#!/usr/bin/python3
# This script sends a notifications to Discord and Bsky for each package that has been updated
# it reads the list of packages from ./packages/updated_packages.txt

import os, time
from datetime import datetime
import requests
import sys

# load discord URL from env secrets
try:
    discordurlEndpoint = os.environ['DISCORD_WEBHOOK_URL']
except KeyError:
    print("DISCORD_WEBHOOK_URL not set in environment variables")
    exit(1)

didLoadBsky = False
try:
    from atproto import Client
    from atproto_client.models import AppBskyEmbedExternal
    didLoadBsky = True
except:
    print("atproto not installed")

if didLoadBsky:
    # load bsky credentials from env secrets
    try:
        bskyAuth = os.environ['BSKY_AUTH']
    except:
        print("BSKY_AUTH not set in environment variables")
        didLoadBsky = False

# we'll fetch all repo data to help construct our embeds
# TODO: redesign the discord embed as well to make use of this info
allRepoData = {}

def fetch_repo_data():
    global didLoadBsky, allRepoData
    allRepoData = {}
    path = "switch"
    data = requests.get(f"https://{path}.cdn.fortheusers.org/repo.json")
    if data.status_code != 200:
        print("Failed to fetch repo data")
        didLoadBsky = False
        return
    if "packages" in data.json():
        packages = data.json()["packages"]
        for idx in range(len(packages)):
            if "name" in packages[idx]:
                allRepoData[packages[idx]["name"]] = packages[idx] # repack as dict

def announce_bsky(package):
    if not didLoadBsky:
        print("bsky not loaded, skipping bsky announcement for", package)
        return
    
    client = Client()
    client.login("hb-app.store", bskyAuth)

    path = "switch"
    url = f"https://hb-app.store/{path}/{package}"
    # fetch the url and pull og:title and og:description
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Failed to fetch URL:", url)
        return

    # fetch and upload the image blob, if it exists
    curData = allRepoData.get(package, {})
    postTitle, postDescription, uploadedBlob = None, None, None
    if curData:
        title = curData.get("title")
        author = curData.get("author")
        description = curData.get("description")
        license = curData.get("license")
        changelog = curData.get("changelog")
        details = curData.get("details")
        version = curData.get("version")

        # build the actual post text content
        if title and author:
            postTitle = f"{title} by {author}"
        if description:
            postDescription = description # short desc
        if license:
            postDescription += f" ({license})"
        if details:
            details = details.replace("\\n", " ")
            details = f"{details[:400]}" + ("..." if len(details) > 400 else "")
        if changelog:
            changelog = changelog.replace("\\n", " ")
            changelog = f"{changelog[:400]}" + ("..." if len(changelog) > 400 else "")

        icon_url = f"https://{path}.cdn.fortheusers.org/packages/{package}/icon.png"
        icon_resp = requests.get(icon_url)
        if icon_resp.status_code == 200:
            uploadedBlob = client.upload_blob(icon_resp.content).blob

    external_link = AppBskyEmbedExternal.External(
        uri=url,
        title=(postTitle + " - " + postDescription) or package, # embed post title has the description as well
        description=changelog or details, # if there's changes, use that instead
        thumb=uploadedBlob,
    )
    embed = AppBskyEmbedExternal.Main(external=external_link)

    # Creating and Sending Post
    post_text = "App Updated: " + (postTitle if postTitle else package) + f" (v{version})"
    client.send_post(text=post_text, embed=embed)
    print("Post with URL successfully sent to Bluesky")

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

fetch_repo_data() # fetch the current repo state first

if len(sys.argv) > 1 and sys.argv[1] == "server":
    # run a cherrypy server that just makes notification announcements
    import cherrypy
    class NotifyServer:
        @cherrypy.expose
        def index(self):
            return "Notify Server is running, listening on port 8111..."

        @cherrypy.expose
        def notify(self, key=None, package=None, bsky=None, discord=None):
            # the key to the accounce key in the env for auth
            if "ANNOUNCE_KEY" not in os.environ:
                return "No announce key set in environment variables"
            announce_key = os.environ["ANNOUNCE_KEY"]
            if key != announce_key:
                return "Invalid announce key"
            fetch_repo_data() # fetch latest repo state first
            if not package:
                return "No package specified"
            if package not in allRepoData:
                return f"Package {package} not found in repo data"
            if bsky:
                announce_bsky(package)
            elif discord:
                announce_discord(package)
            else:
                return "No announce method specified"
            return f"Notification sent for {package}"

    cherrypy.config.update({'server.socket_port': 8111})
    cherrypy.quickstart(NotifyServer(), '/', {'/': {}})
    exit(0)

with open("packages/updated_packages.txt") as f:
    packages = f.read().split(",")
    for package in packages:
        package = package.strip()
        if package:
            status_code = announce_discord(package)
            announce_bsky(package)
            if status_code == 204:
                print(f"Notification sent for {package}")
            else:
                print(f"Failed to send notification for {package}, status code: {status_code}")