#!/usr/local/env python3
# This is a helper script to create a new package folder with a default pkgbuild.json,
# with pre-populated fields from the current live repo.json file.

import requests
import json
import os, sys
import base64

if len(sys.argv) < 2:
    print("Usage: python3 stage_update.py <package_name>")
    sys.exit(1)

package = sys.argv[1]

# download the current repo
REPO = "https://switch.cdn.fortheusers.org"
response = requests.get(f"{REPO}/repo.json")
if response.status_code != 200:
    print("Failed to download repo.json")
    sys.exit(1)
repo = response.json()

# get the existing libget package data from the repo
data = [pkg for pkg in repo["packages"] if pkg["name"] == package]

# create the new package folder
os.makedirs(f"packages/{package}", exist_ok=True)

# TODO: if we have some pkgbuild.json data already, persist it here for convenience

# build the template pkgbuild.json
template = {
    "package": package,
    "info": {
        "title": "",
        "author": "",
        "category": "",
        "version": "",
        "url": "",
        "license": "",
        "description": "",
        "details": "",
    },
    "changelog": "",
    "assets": [],
}

if len(data) == 0:
    # try and log into the package submission endpoint to see if we have any submitted matches
    notFound = False
    with open("creds.json") as creds:
        creds = json.load(creds)
        endpoint = creds["submissionEndpoint"]
        username = creds["submissionUsername"]
        authkey = creds["submissionAuthkey"]
        if not endpoint or not username or not authkey:
            print("No credentials found for package submission endpoint")
            notFound = True
        else:
            response = requests.get(f"{endpoint}", auth=(username, authkey))
            if response.status_code != 200:
                print("Failed to download recent submissions")
                notFound = True
            else:
                data = [pkg for pkg in response.json() if pkg["pkg"]["package"] == package]
                if len(data) == 0:
                    notFound = True
                else:
                    # we found some package data, populate the template
                    with open(f"packages/{package}/pkgbuild.json", "w") as f:
                        # delete some keys that we don't need from the submission template
                        pkgData = data[0]["pkg"]
                        if "changes" in pkgData:
                            pkgData["changelog"] = pkgData["changes"] # handle legacy key
                            del pkgData["changes"]
                        if "console" in pkgData:
                            del pkgData["console"]
                        if "submitter" in pkgData:
                            del pkgData["submitter"]
                        if "type" in pkgData:
                            del pkgData["type"]
                        # also, if we have any base64 assets, convert them to files
                        if "assets" in pkgData:
                            for asset in pkgData["assets"]:
                                if "format" in asset and "data" in asset and asset["format"] == "base64":
                                    b64data = asset["data"]
                                    asset["url"] = asset["type"] + ".png"
                                    with open(f"packages/{package}/{asset['url']}", "wb") as img:
                                        # remove base URI prefix
                                        b64data = b64data.split(",")[1]
                                        img.write(base64.b64decode(b64data))
                                # always delete format and data keys
                                if "format" in asset:
                                    del asset["format"]
                                if "data" in asset:
                                    del asset["data"]
                        # write the template to the new package folder 
                        json.dump(pkgData, f, indent=4)
                        print(f"Created new package folder for {package} in packages from recent submissions")
    if notFound:
        print(f"Package {package} not found in repo.json, or recent submissions, making empty pkgbuild.json")
        with open(f"packages/{package}/pkgbuild.json", "w") as f:
            json.dump(template, f, indent=4)
    sys.exit(0)

data = data[0] # grab first match for this package name

# for each key in the template, copy the data from the repo
for key in template["info"]:
    if key in data:
        template["info"][key] = data[key]
if "changelog" in data:
    template["changelog"] = data["changelog"]

# create the initial assets, assuming a simple file, or simple extract
template["assets"].append({
    "url": "https://example.com/file.zip",
    "type": "zip",
    "zip": [{
        "path": "/**/*",
        "dest": "/",
        "type": "update",
    }]
})

template["assets"].append({
    "url": "https://example.com/file.nro",
    "dest": data["binary"] if "binary" in data else "/switch/path/etc.nro",
    "type": "update",
})

# try to download the assets and any screen shots
screensCount = data["screens"]
screenSlugs = [f"screen{i}" for i in range(1, screensCount + 1)]
dlUrls = [f"{REPO}/packages/{package}/{name}.png" for name in ["icon", "screen"] + screenSlugs]

for url in dlUrls:
    response = requests.get(url)
    if response.status_code == 200:
        fileName = os.path.basename(url)
        with open(f"packages/{package}/{fileName}", "wb") as f:
            f.write(response.content)
            assetType = "screenshot"
            if fileName == "icon.png":
                assetType = "icon"
            if fileName == "screen.png":
                assetType = "banner"
            # wrote the file, update our template assets
            template["assets"].append({
                "type": assetType,
                "url": fileName,
            })

# write the template to the new package folder
with open(f"packages/{package}/pkgbuild.json", "w") as f:
    json.dump(template, f, indent=4)

print(f"Created new package folder for {package} in packages")