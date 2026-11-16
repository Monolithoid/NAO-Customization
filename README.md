# NAO Customization

Small customizations for my Linux, Windows, and other environments.
Each customization is self-contained: its files, prerequisites, and instructions
live in its own directory.

## Project structure

```text
linux/
  gdm/
    nao-background/ # Native Ubuntu background and optional colors
    nao/            # Full login theme (installation suspended)
  plymouth/
    nao-bounce/    # Prototype: NAO bounces during boot
    nao-dance/     # Transparent arm-wave animation and preview
windows/          # Future Windows customizations
shared/           # Resources shared across systems
```

## First project

[NAO Bounce](linux/plymouth/nao-bounce/README.md) is a starter Plymouth theme.
It uses a placeholder robot mascot that can be replaced with the actual NAO artwork.

A [short dance reference](linux/plymouth/nao-dance/README.md) is also available,
with a transparent arm-wave image sequence and looping previews.

## Login screen

[NAO background](linux/gdm/nao-background/README.md) changes only the wallpaper
using Ubuntu's native login-screen settings, with an optional dark preference
and blue accent.

[NAO GDM](linux/gdm/nao/README.md) contains the earlier full login-screen design.
Installation is suspended following a reported GDM regression; use its recovery
instructions to restore an existing installation.

## Adding a customization

Create a directory under the relevant system, such as `linux/terminal/my-theme`
or `windows/terminal/my-theme`. Add a README describing the intended result,
prerequisites, installation, verification, and uninstallation. Keep project-specific
resources in its `assets/` directory; reserve `shared/` for resources used by
multiple projects. Do not commit secrets or personal configuration containing
credentials.
