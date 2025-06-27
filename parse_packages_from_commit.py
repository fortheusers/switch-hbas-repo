#!/usr/local/env python3
# This is a helper script to list any packages that match text in the last commit message
# it writes the list to packages_in_commit.txt

import os, sys

# get a list of all packages from ./packages
packages = os.listdir("./packages")
out = set()

if len(sys.argv) < 2:
    print("Usage: python3 parse_packages_from_commit.py <commit_message>")
    sys.exit(1)

commit_message = sys.argv[1]
for package in packages:
    if package in commit_message:
        out.add(package)

# if we have a match for skip_notify, pass it through
if "skip_notify" in commit_message:
    out.add("skip_notify")

# if we have a match for the force_refresh_all keyword, add all packages
if "force_refresh_all" in commit_message:
    out = set(packages)

with open("packages_in_commit.txt", "w") as f:
    for package in out:
        f.write(package + "\n")

print("Wrote to packages_in_commit.txt, count:", len(out))