# NAO Customization

Small customizations for my Linux, Windows, and other environments.
Each customization is self-contained: its files, prerequisites, and instructions
live in its own directory.

## Project structure

```text
linux/
  plymouth/
    nao-bounce/    # Prototype: NAO bounces during boot
    nao-dance/     # Short arm-wave clip and looping preview
windows/          # Future Windows customizations
shared/           # Resources shared across systems
```

## First project

[NAO Bounce](linux/plymouth/nao-bounce/README.md) is a starter Plymouth theme.
It uses a placeholder robot mascot that can be replaced with the actual NAO artwork.

A [short dance reference](linux/plymouth/nao-dance/README.md) is also available,
with an extracted arm-wave cycle and a looping preview.

## Adding a customization

Create a directory under the relevant system, such as `linux/terminal/my-theme`
or `windows/terminal/my-theme`. Add a README describing the intended result,
prerequisites, installation, verification, and uninstallation. Keep project-specific
resources in its `assets/` directory; reserve `shared/` for resources used by
multiple projects. Do not commit secrets or personal configuration containing
credentials.
