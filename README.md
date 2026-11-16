# NAO Customization

Small customizations for my Linux, Windows, and other environments.
Each customization is self-contained: its files, prerequisites, and instructions
live in its own directory.

## Project structure

```text
linux/
  gdm/
    nao-background/ # Native Ubuntu background and optional colors
  plymouth/
    nao-dance/      # Transparent NAO boot animation
windows/            # Future Windows customizations
shared/             # Resources shared across systems
```

## Boot animation

[NAO Dance](linux/plymouth/nao-dance/README.md) is a Plymouth theme using a short,
transparent arm-wave loop. It includes installation and restoration instructions,
source footage, exported frames, and looping previews.

## Login screen

[NAO background](linux/gdm/nao-background/README.md) customizes Ubuntu's login
screen with native background settings and optional dark preference and blue
accent. Background and colors can be restored independently.

The abandoned full GDM theme and initial placeholder Plymouth prototype have
been removed. Recovery instructions for legacy GDM installations are available
in the [login-screen README](linux/gdm/nao-background/README.md#legacy-gdm-recovery).

## Adding a customization

Create a directory under the relevant system, such as `linux/terminal/my-theme`
or `windows/terminal/my-theme`. Add a README describing the intended result,
prerequisites, installation, verification, and uninstallation. Keep project-specific
resources in its `assets/` directory; reserve `shared/` for resources used by
multiple projects. Do not commit secrets or personal configuration containing
credentials.
