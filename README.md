## 4TU HBAS Repo for Switch
This git repository contains package metadata that generates the libget repo published at [switch.cdn.fortheusers.org](https://switch.cdn.fortheusers.org/repo.json).

The syntax of the pkgbuild.json files here are defined in the [spinarak](https://github.com/fortheusers/spinarak) project README.

The packages listed here in the `packages` folder are merged with the older manually managed repo. The [Magnezone](https://github.com/fortheusers/magnezone) README details further how this primary/secondary repo sourcing works. Our long term goal though is to have all packages going forward be managed by pkgbuild metadata in this repo.

### Contributing
If you want to add a new, or update an existing app, please feel free to open a [Pull request](https://github.com/fortheusers/switch-hbas-repo/pulls) with your changes!

The metadata within this repo is available to use under a [CC-BY-SA license](https://creativecommons.org/licenses/by-sa/4.0/deed.en).

**TODO:** More detailed documentation on `pkgbuild.json` still needs to be written. For now, the recommendation is to check other existing [switch-repo packages](https://github.com/fortheusers/switch-hbas-repo/tree/main/packages) to understand the syntax and layout.

### Testing your pkgbuild.json
First, clone the repo recursively:
```
git clone --recursive https://github.com/fortheusers/switch-hbas-repo
cd switch-hbas-repo
```

Then, remove _all_ of the packages in the packages folder (otherwise, spinarak will build all of them, which is not necessary)

```
rm -rf packages
mkdir packages
cd packages
```

Then create your pkgbuild.json and any other assets within a new folder inside of `packages`.

After your package is created, run spinarak _from the `packages` folder_ as the current directory.

```
pip3 install -r ../spinarak/requirements.txt
python3 ../spinarak/spinarak.py
```

This should report that one package is detected (your folder name, within `packages`) and try to build it, by downloading whatever assets are present. It will also print out the manifest contents for debugging purposes. If successful, you should get your built package zip in `public/zips`, as well as a `public/repo.json` with one entry in it.

**Notice:** Spinarak, while building will add additional files to your package's folder prior to zipping. These can be exluded in your PR. 

**TODO:** An automated script that can test JSON files, and print out the manifest structure, without needing to mess around with the filesystem.

### Using stage_update.py

If your package is already on the non-metadata Switch repo, run: `python3 stage_update.py <YourPackageName>` to create an initial `pkgbuild.json` and assets with most information filled out automatically.

**TODO:** This repo contains copied files from `switch-hbas-repo`, these scripts should be consolidated in the future.
