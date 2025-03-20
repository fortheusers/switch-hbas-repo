#!/usr/local/env python3
# This is a helper script to list any packages that match text in the last commit message
# it writes the list to packages_in_commit.txt

import os, subprocess

# get a list of all packages from ./packages
packages = os.listdir("packages")
out = set()

commit_message = subprocess.run(["git", "log", "-1"], capture_output=True, text=True).stdout
for package in packages:
    if package in commit_message:
        out.add(package)

# if we have a match for the force_refresh_all keyword, add all packages
if "force_refresh_all" in commit_message:
    out = set(packages)

with open("packages_in_commit.txt", "w") as f:
    for package in out:
        f.write(package + "\n")