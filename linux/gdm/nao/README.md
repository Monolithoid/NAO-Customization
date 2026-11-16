# NAO login screen — installation suspended

The first installation was reported to change the login screen unexpectedly,
show a technical-looking account (reported approximately as "GDM Keeper"), and
change the apparent session/startup environment. The cause has not been confirmed
from target-machine logs. New CLI installations are disabled until the regression
has been diagnosed and the theme has been tested in an actual Ubuntu 26.04 /
GNOME Shell 50.1 GDM session.

## Identified profile handling defect

Inspection of Ubuntu's gdm3 50.1 package revealed that its vendor profile at
`/usr/share/dconf/profile/gdm` contains:

```text
user-db:user
file-db:/var/lib/gdm3/greeter-dconf-defaults
```

When `/etc/dconf/profile/gdm` was absent, the first installer created an override
with `user-db:user` and `system-db:gdm`, masking the vendor profile and omitting
the compiled greeter defaults. That is a confirmed defect in the installer and a
probable explanation for the reported session changes, conditional on the target
machine having used the vendor profile. The exact runtime failure has not been
reproduced. Forcing the user list was another unnecessary configuration change.

The [background-only variant](../nao-background/README.md) uses Ubuntu's native
background keys and existing configuration generator, preserving the profile.
The full-theme installation remains disabled.

## Restore the previous configuration first

From the repository root:

```sh
git pull --ff-only
cd linux/gdm/nao
sudo python3 install.py --restore
```

The original version of `--restore` can also restore the saved configuration;
updating first includes support for retrying after a failed dconf database update.
Do not delete `/var/lib/nao-gdm`: it contains the original entries and profile.

The restore operation returns the GDM resource entry (including its original
symlink, if present), the GDM dconf profile, and the NAO settings file to their
saved states, then rebuilds the dconf database. It never restarts GDM. Save any
open work before logging out or rebooting to reload the restored configuration.
Locking the screen does not necessarily reload the greeter theme.

If graphical login is unavailable, switch to a text console with Ctrl+Alt+F3,
log in with your normal account, change to the checkout and run the same command.
Do not delete or rename system accounts in an attempt to fix this symptom.

If restoration reports that a file changed after installation, keep the error and
backup for diagnosis. The script deliberately refuses to overwrite intervening
administrator or package changes. If the dconf update fails after files have
been restored, the backup is retained and the operation can be retried.

## What the attempted installation changed

- `/usr/share/gnome-shell/gdm-theme.gresource`: replaced the named entry with a
  rebuilt theme, preserving the vendor target if the entry was a symlink.
- `/etc/dconf/profile/gdm`: created or extended the profile to include `system-db:gdm`.
- `/etc/dconf/db/gdm.d/99-nao-login`: set the logo to an empty string and initially
  forced `disable-user-list=false`. That user-list override has now been removed
  from the code. This code change does not undo an existing installation; restore
  the saved configuration on the target machine.
- Ran `dconf update` and stored backups in `/var/lib/nao-gdm`.

The script contains no account creation, display-manager switching, session
installation, bootloader or initramfs commands. The reported account and session
change still require target-machine diagnosis; this list does not establish a
root cause or prove that the screen can be safely customized with this approach.

## Diagnosis after recovery

Report the restoration command's output and whether the normal login screen
returns. Distinguish the login screen, lock screen, and desktop after login.
If the symptom persists, useful read-only evidence includes:

```sh
systemctl status display-manager --no-pager
journalctl -b -u gdm3 --no-pager -n 80
```

## Design and build-only mode

The intended design remains a large, static NAO on the right, the user selector
and password prompt on the left, a dark blue background with cyan accents, and
no distribution logo. Default geometry is 1920 × 1080 at 100% scale.

`preview.html` is an approximate browser mockup with fictional accounts; it does
not authenticate users or emulate GDM. The artwork is a 300 × 360 transparent
frame from the user-provided dance clip, so enlarged rendering may look soft.
Source: https://www.youtube.com/watch?v=2laujomh0JY&t=333s
No ownership or redistribution license is asserted for the footage.

Build-only mode remains available for investigation without installation. It
requires `python3`, `gresource` and `glib-compile-resources`:

```sh
python3 install.py --output /tmp/nao-gdm.gresource
```

Do not manually copy this experimental resource into system directories.

## Validation limits

Nine automated tests check resource compilation, binary asset preservation,
light/dark CSS variants, reversible file and symlink changes, existing profile
preservation, rollback, retry after a failed restore database update, later-change
protection, user-list policy preservation and the CLI installation block.

```sh
python3 -m unittest discover -s tests -v
```

Installation tests run in temporary directories with GNOME and dconf calls
simulated. They do not validate GDM rendering, authentication, account filtering,
session selection, or Ubuntu integration. Passing them does not establish runtime
compatibility. The cloud workspace cannot access the user's Ubuntu machine.
