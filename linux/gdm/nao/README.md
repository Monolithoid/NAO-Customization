# NAO login screen — GDM

For Ubuntu 26.04 LTS, GNOME Shell 50.x and a **1920 × 1080 primary display at
100% scale**. NAO appears large and static on the right; the user selector and
password prompt use the left half. The dark blue background and cyan accents
match the Plymouth theme. The GDM distribution logo is disabled.

## Install

From your existing checkout, update the branch containing this theme:

```sh
git switch feat/customization-project-structure
git pull --ff-only
cd linux/gdm/nao
sudo apt install python3 libglib2.0-dev-bin dconf-cli
sudo python3 install.py
```

The installer reads `/usr/share/gnome-shell/gdm-theme.gresource`, preserves all
original resource entries and appends the NAO styling to its CSS variants. It
adds the transparent PNG to the resource, compiles and verifies the new bundle,
then replaces only the GDM resource entry. If that entry was a symlink to a
shared vendor theme, the vendor target is left unchanged. The running desktop's
theme is not replaced.

The installer adds `/etc/dconf/db/gdm.d/99-nao-login` with `logo=''` and
`disable-user-list=false`. It preserves the existing GDM dconf profile, adding
`system-db:gdm` if needed. Existing user accounts and authentication are managed
by GDM as before. Accessibility and session-selection controls remain available,
although the latter follow the left-column layout.

Backups of replaced entries and the profile are stored in `/var/lib/nao-gdm`.
A second installation refuses to overwrite the backup: restore first to change
settings or refresh the theme. Installation errors trigger rollback. The installer
never restarts GDM or rebuilds the initramfs.

**Save your work and log out** to see the result. Use a real logout rather than
locking the desktop: the GNOME lock screen is separate. GDM may require a new
session or a reboot to reload its theme resource; do not restart the service
while graphical sessions contain unsaved work.

## Restore

From this directory, run:

```sh
sudo python3 install.py --restore
```

The original GDM resource entry (including its symlink, if any), settings file
and profile are restored, then the dconf database is rebuilt. Restore refuses to
overwrite changes made after installation and keeps the backup for manual review.
If a later package update has changed these entries, consult the backup instead
of forcing an old resource over the updated version.

If the graphical login fails, switch to a text console with Ctrl+Alt+F3, log in,
change to this directory and run the same restoration command. Then reboot when
appropriate. Keep this checkout available until the theme has been tested.

## Display size

GNOME's St CSS does not support percentage padding. The installer uses the
primary display's physical dimensions and scale to generate a fixed two-column
layout. Its default is 1920 × 1080 at 100% (the requested configuration). To use
another geometry, restore and reinstall, for example:

```sh
sudo python3 install.py --width 2560 --height 1440 --scale 1
```

Use GDM's scale, which may differ from the signed-in desktop's scale. Multi-monitor,
portrait and changing-resolution layouts have not been validated. The minimum
supported logical area is 960 × 540, with at least 1280 × 720 physical pixels.

## Build without installing

To check resource compatibility and compilation on the target machine without
changing system files:

```sh
python3 install.py --output /tmp/nao-gdm.gresource
```

This validates the resource structure and build, not the rendered login screen.
`preview.html` is an approximate browser mockup with fictional accounts, not a
GDM emulator or an authentication form. It does not reproduce GNOME's exact
widget sizing or rendering.

## Artwork and branding

`assets/nao.png` is a static transparent frame from the user-provided dance clip.
Its source resolution is 300 × 360; enlarged rendering may look soft. Source:
https://www.youtube.com/watch?v=2laujomh0JY&t=333s
No ownership or redistribution license is asserted for this footage.

Logo removal is scoped to the login-screen distribution logo. The installer does
not rename the operating system, packages or existing session names such as
"Ubuntu" in the session chooser. Theme/package upgrades may reset the GDM entry;
the installer is not a permanent replacement for distribution maintenance.

## Validation

Six automated tests compile real GResource bundles and exercise preservation of
binary assets, light/dark CSS variants, symlink and regular-file installation and
restoration, profile preservation, rollback after a failed dconf update, and
refusal to overwrite subsequent administrator changes or unknown resources.
GNOME/dconf calls in installation tests are simulated; no real GDM session is
modified by the tests.

```sh
python3 -m unittest discover -s tests -v
```

The left-column layout follows GNOME Shell 50's `loginDialog.js` content-box
allocation and uses properties supported by St's CSS parser. GNOME Shell 50.1
and Ubuntu 26.04 are not available in the cloud workspace: actual rendering,
authentication and accessibility must still be checked on the target machine.
