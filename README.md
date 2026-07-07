[![Pyversions](https://img.shields.io/pypi/pyversions/maestral.svg)](https://pypi.org/pypi/maestral/)

> **Fork notice**
>
> `maestral-gagnant` is a maintained fork of [Maestral](https://github.com/SamSchott/maestral)
> by Sam Schott, which was archived on 2026-07-28. This fork continues development of the
> light-weight, open-source Dropbox client. All credit for the original work goes to the
> upstream author and contributors.

# Maestral <img src="https://raw.githubusercontent.com/izo/maestral-gagnant/main/src/maestral/resources/maestral.png" align="right" title="Maestral" width="110" height="110">

A light-weight and open-source Dropbox client for macOS and Linux.

## About

Maestral is an open-source Dropbox client written in Python. The project's main goal is to
provide a client for platforms and file systems that are no longer directly supported by
Dropbox.

Maestral currently does not support Dropbox Paper, the management of Dropbox teams, and
the management of shared folder settings. If you need any of this functionality, please
use the Dropbox website or the official client. Maestral does support syncing
multiple Dropbox accounts and excluding local files from sync with a ".mignore" file.

The focus on "simple" file syncing does come with advantages: on macOS, the Maestral App
bundle is significantly smaller than the official Dropbox app and uses less memory. The
exact memory usage will depend on the size of your synced Dropbox folder and can be further
reduced when running Maestral without a GUI.

Maestral uses the public Dropbox API which, unlike the official client, does not support
transferring only those parts of a file which changed ("binary diff"). Maestral may
therefore use more bandwidth that the official client. However, it will avoid uploading
or downloading a file if it already exists with the same content locally or in the cloud.

## Warning

- Never sync a local folder with both the official Dropbox client and Maestral at the same
  time.
- Network drives and some external hard drives are not supported as locations for the
  Dropbox folder.

## Installation

This fork is installed from source. It is recommended to install it inside a virtual
environment as follows:

```console
$ python3 -m venv maestral-venv
$ source maestral-venv/bin/activate
(maestral-venv)$ python3 -m pip install --upgrade 'git+https://github.com/izo/maestral-gagnant.git'
```

The command line entry point remains `maestral`. For general setup, system requirements
and CLI reference, the original [Maestral documentation](https://maestral.app/docs) still
applies to this fork.

> **GUI note:** the upstream `maestral-qt` (Linux) and `maestral-cocoa` (macOS) frontends
> depend on the upstream `maestral` distribution and may conflict with this fork. Prefer
> running the fork headless (`maestral start`) until fork-specific GUI packages are
> available.

### Docker image

You can build a Docker image locally from the included `Dockerfile`:

```console
$ docker build -t maestral-gagnant .
```

## Usage

Run `maestral gui` in the command line (or open the Maestral app on macOS) to start
Maestral with a graphical user interface. On its first run, Maestral will guide you
through linking and configuring your Dropbox and will then start syncing.

<img src="https://raw.githubusercontent.com/izo/maestral-gagnant/main/screenshots/macOS_dark.png" alt="screenshot macOS" width="840"/>
<img src="https://raw.githubusercontent.com/izo/maestral-gagnant/main/screenshots/Ubuntu.png" alt="screenshot Fedora" width="840"/>

### Command line usage

After installation, Maestral will be available as a command line script by typing
`maestral` in the command prompt. Type `maestral --help` to get a full list of available
commands. The most important are:

- `maestral gui`: Starts the Maestral GUI. Creates a sync daemon if not already running.
- `maestral start|stop`: Starts or stops the Maestral sync daemon.
- `maestral pause|resume`: Pauses or resumes syncing.
- `maestral autostart -Y|-N`: Sets the daemon to start on log in.
- `maestral status`: Gets the current status of Maestral.
- `maestral filestatus LOCAL_PATH`: Gets the sync status of an individual file or folder.
- `maestral excluded add|remove|list`: Command group to manage excluded folders.
- `maestral ls DROPBOX_PATH`: Lists the contents of a directory on Dropbox.
- `maestral notify snooze N`: Snoozes desktop notifications for N minutes.

Maestral supports syncing multiple Dropbox accounts by running multiple instances
with different configuration files. This needs to be configured from the command
line by passing the option `--config-name` to `maestral start` or `maestral gui`.
Maestral will then select an existing config with the given name or create a new one.
For example:

```console
$ maestral start --config-name="personal"
$ maestral start --config-name="work"
```

This will start two instances of Maestral, syncing a private and a work account,
respectively. Configs will be automatically cleared when unlinking an account. You can
list all currently linked accounts with `maestral config-files`. The above setup for
example will return the following on macOS:

```console
$ maestral config-files

Config name  Account          Path
maestral     user@gmail.com   ~/Library/Application Support/maestral/maestral.ini
private      user@mycorp.org  ~/Library/Application Support/maestral/private.ini
```

By default, the Dropbox folder names will contain the capitalised config-name in braces.
In the above case, this will be "Dropbox (Personal)" and "Dropbox (Work)".

A full documentation of the CLI is available on the
[website](https://maestral.app/cli).

## Contribute

There are multiple topics that could use your help. Some of them are easy, such as adding
new CLI commands, others require more experience, such as packaging for non-macOS
platforms. Look out for issues marked with "good first issue" or "help wanted".

Relevant resources are:

- [Maestral API docs](https://maestral.readthedocs.io)
- [Dropbox API docs](https://www.dropbox.com/developers/documentation/http/documentation)
- [Dropbox Python SDK docs](https://dropbox-sdk-python.readthedocs.io/en/latest/)

[CONTRIBUTING.md](CONTRIBUTING.md) contains detailed information on the expected code
style and test format.

## System requirements

- macOS 10.15 Catalina or higher or Linux
- Python 3.10 or higher
- For the system tray icon on Linux:
  - [gnome-shell-extension-appindicator](https://github.com/ubuntu/gnome-shell-extension-appindicator)
    on Gnome 3.26 and higher
