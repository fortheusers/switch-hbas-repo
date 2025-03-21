#!/usr/local/env python3
# This is a helper script to create a new package folder with a default pkgbuild.json,
# with pre-populated fields from the current live repo.json file.

import requests
import json
import os, sys

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
    print(f"Package {package} not found in repo.json, make empty pkgbuild.json")
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
        "path": "/**",
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