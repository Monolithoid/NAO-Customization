# NAO login screen — GDM design

Target: Ubuntu 26.04 LTS with GDM3.

## Intended appearance

- A large, static NAO robot on the right.
- The real GDM user selector and authentication prompt on the left.
- The dark blue palette used by the NAO Plymouth theme, with a cyan accent.
- No Ubuntu logo or distribution branding on the login screen.

`preview.html` is a local design preview with fictional accounts. Open it in a
browser directly; it does not authenticate users or change GDM. The installed
screen should keep the machine's real user names and language, as well as GDM's
keyboard, accessibility, session selection, and power controls.

`assets/nao.png` is a static transparent frame from the user-provided dance clip.
Its source resolution is 300 × 360; enlarged rendering may look soft. Source:
https://www.youtube.com/watch?v=2laujomh0JY&t=333s
No ownership or redistribution license is asserted for this footage.

## Implementation status

The GDM theme is not yet installable. The installed GNOME Shell version and
Ubuntu GDM resource/alternative paths must be identified before implementing
installation and restoration. Upstream GNOME Shell calculates the user-selector
and password-prompt positions in `js/gdm/loginDialog.js`; ordinary desktop
wallpaper settings do not implement this layout.

Run on the target machine and report the output:

```sh
gnome-shell --version
readlink -f /usr/share/gnome-shell/gdm-theme.gresource
update-alternatives --query gdm-theme.gresource
ls -l /usr/share/gnome-shell/*gresource*
```

An absent path or alternative is useful diagnostic information, not a reason to
create it manually. Do not install the HTML preview as a greeter or restart GDM
from a logged-in desktop session: restarting GDM ends graphical sessions.

The eventual installation must preserve the original theme and document a
restoration path. Removing branding is scoped to the login screen; it does not
rename the operating system, installed packages, or session definitions.

## Validation

The preview and static image can be inspected independently. No GDM runtime or
Ubuntu 26.04 desktop is available in the cloud workspace. Actual login behavior,
layout, accessibility and restoration remain untested.
