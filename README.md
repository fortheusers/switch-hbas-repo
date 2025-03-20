## 4TU HBAS Repo for Switch
This git repository contains package metadata that generates the libget repo published at [switch.cdn.fortheusers.org](https://switch.cdn.fortheusers.org/repo.json).

The syntax of the pkgbuild.json files here are defined in the [spinarak](https://github.com/fortheusers/spinarak) project README.

If a package folder is missing here, but you can see it on [hb-app.store](https://hb-app.store), then it's being maintained manually on our secondary repo. In this case, the `stage_update.py` script (see below) can be used to help migrate existing package data to this files in this repo.

The [Magnezone](https://github.com/fortheusers/magnezone) README details further how this primary/secondary repo sourcing works. Our long term goal though is to have all packages going forward be managed by pkgbuild metadata in this repo.

### Contributing
If you want to add a new, or update an existing app, please feel free to open a [Pull request](https://github.com/fortheusers/switch-hbas-repo/pulls) with your changes!

The metadata within this repo is available to use under a [CC-BY-SA license](https://creativecommons.org/licenses/by-sa/4.0/deed.en).

### pkgbuild info
The `assets` section of the pkgbuild.json contains info about how to source the files that will end up in the zip, as well as to which paths they will be downloaded to. This allows for a mapping of URLs to specific folders on the SD card, after downloading.

For an explanation of the different extraction states (Install, Extract, Update, Get), see the [libget Wiki](https://github.com/fortheusers/libget/wiki/Overview-&-Glossary). Concisely, most files will use the `update` state, which indicates that the file should always be extracted on update or install of the package.

### CI Updates
If the `version` key is bumped, the package will be rebuilt by the CI, including the re-sourcing and re-downloading of any required assets. See the [Spinarak Wiki](https://gitlab.com/4TU/spinarak/-/wikis/pkgbuild.json-specification) for more detailed information on pkgbuild keys and assets.

If the `version` key is not bumped, you can still force a manual update by including the name of the package in your git commit. Eg. if my commit message was "fix file layout issue in vgedit", the precesense of the string `vgedit` in the commit will ensure that the package is rebuilt.

### Migration script
For migrating an existing package into a pkgbuild, you can run `python3 stage_update.py <package name>` and a template directory, pkgbuild.json, and assets will be created. It includes both an example for extracting a zip, or a simple one-file download.

For zip extractions, in most cases there should not be a trailing slash on the `dest` key, or there will be double-slash'd paths in the manifest. If the same file path is matched by another asset, (see McOsu-NX package for an example), the later assets will override the state in the earlier assets. This allows for the first asset to be "extract all, with `update` type" and then the second one to be "extract just songs, with `get` type".