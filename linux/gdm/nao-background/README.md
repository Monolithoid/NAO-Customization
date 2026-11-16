# NAO GDM background — native Ubuntu settings

Change only the login-screen background on Ubuntu 26.04. The wallpaper has a
static NAO on the right over the Plymouth dark blue palette. The existing login
form, account visibility, logo, session selection and theme retain their settings.

This uses Ubuntu's native `com.ubuntu.login-screen` background keys. It does not
rebuild GResource bundles or create or edit a GDM dconf profile. The earlier full
GDM theme installer in `../nao` remains suspended.

## Install

From the root of the existing checkout:

```sh
git pull --ff-only
cd linux/gdm/nao-background
sudo python3 install.py
```

Python 3, GSettings, dconf and the Ubuntu GDM configuration generator must already
be installed. Restore the earlier experimental full theme first if its backup
still exists. The script checks the active GDM profile and native schema keys;
if the expected Ubuntu configuration is absent, it stops without changing it.

Save your work and log out to inspect the login screen, or reboot. Locking the
desktop is not the same test. The installer does not restart GDM.

## Restore the previous background

From this directory:

```sh
sudo python3 install.py --restore
```

Only this installer's wallpaper and background override are removed. The normal
GDM configuration generator is rerun. Later modifications to those files are
protected: the script stops and retains its recovery record rather than deleting
them. Recovery records live in `/var/lib/nao-gdm-background`.

## Mechanism

The installer adds:

- `/usr/local/share/nao-gdm-background/nao-background.svg`, a self-contained image.
- `/usr/share/gdm/dconf/99-nao-background`, with just these three keys:

```ini
[com/ubuntu/login-screen]
background-picture-uri='file:///usr/local/share/nao-gdm-background/nao-background.svg'
background-size='cover'
background-repeat='no-repeat'
```

It then runs `/usr/share/gdm/generate-config`, the generator shipped by Ubuntu.
This compiles the existing source directory, including upstream settings and the
administrator's `90-debian-settings`, into the usual greeter defaults database.
The helper may signal the greeter's dconf service to reload; it does not restart
GDM or end the signed-in user's graphical session.

The existing profile must retain
`file-db:/var/lib/gdm3/greeter-dconf-defaults`. Its contents are never rewritten.
No changes to logos, users, authentication, accounts, theme CSS or boot settings
are included. Existing per-user overrides or administrator locks can take
precedence over these defaults; report that situation instead of forcing changes.

## Evidence and limits

The mechanism was checked against the official Ubuntu packages:

- [gnome-shell-common 50.1-0ubuntu1.5](https://archive.ubuntu.com/ubuntu/pool/main/g/gnome-shell/gnome-shell-common_50.1-0ubuntu1.5_all.deb): native schema and supported background values.
- [GNOME Shell Ubuntu patches](https://archive.ubuntu.com/ubuntu/pool/main/g/gnome-shell/gnome-shell_50.1-0ubuntu1.5.debian.tar.xz): native background settings applied by ScreenShield.
- [gdm3 50.1-0ubuntu0.1](https://archive.ubuntu.com/ubuntu/pool/main/g/gdm3/gdm3_50.1-0ubuntu0.1_amd64.deb): vendor profile, default settings and configuration generator.

Five tests compile and read real dconf databases in temporary directories. They
verify that background values change, the login-session defaults and vendor
profile remain intact, restoration returns the original defaults, errors roll
back the added files, and custom profiles/later changes are protected.

```sh
python3 -m unittest discover -s tests -v
```

These tests do not launch GDM. The cloud host is Debian and cannot validate the
rendered Ubuntu login screen or authentication. The SVG was rendered and visually
inspected separately. On-machine visual validation is still required.

## Artwork

The background is designed for 1920 × 1080; `cover` scales it on other displays.
It embeds a static transparent 300 × 360 frame from the user-provided NAO video,
so the enlarged robot has limited detail. Source:
https://www.youtube.com/watch?v=2laujomh0JY&t=333s
No ownership or redistribution license is asserted for the footage.
