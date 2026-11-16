# NAO Bounce — Plymouth prototype

A robot mascot bounces in the center of a dark blue background during boot.
The included PNG is placeholder artwork created for this repository, not official
NAO artwork. Replace `assets/nao.png` with a transparent PNG of similar dimensions
(192 × 192) to customize the character. Adjust the motion in `nao-bounce.script`:
amplitude `45`, speed `3`.

## Prerequisites

A Linux machine running Plymouth with its `script` plugin. Package names and theme
selection tools depend on the distribution. No secrets or external services are
required. This theme is for Linux only.

## Manual installation

From this directory, on a test machine with Plymouth installed:

```sh
sudo install -d /usr/share/plymouth/themes/nao-bounce
sudo install -m 644 nao-bounce.plymouth nao-bounce.script assets/nao.png /usr/share/plymouth/themes/nao-bounce/
```

Theme selection and initramfs rebuilding are distribution-specific. Record the
current theme before making any changes.

On distributions providing `plymouth-set-default-theme`:

```sh
plymouth-set-default-theme                 # Record this value for restoration
sudo plymouth-set-default-theme -R nao-bounce
```

On Debian/Ubuntu systems using alternatives:

```sh
update-alternatives --display default.plymouth   # Record the current target
sudo update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/nao-bounce/nao-bounce.plymouth 100
sudo update-alternatives --config default.plymouth
sudo update-initramfs -u
```

## Verification

Check the rendering in a VM with a graphical console before using this prototype
on your main machine. Check the animation, messages, and, where applicable, disk
unlock password entry. Plymouth depends on the console and graphics hardware:
serving these files in a browser does not test the theme.
Rendering and these interactions have not yet been validated in Plymouth.

## Uninstallation

Restore the previous theme and rebuild the initramfs using your distribution's
method. With alternatives, select the previous target first, then remove this
theme's registration:

```sh
sudo update-alternatives --remove default.plymouth /usr/share/plymouth/themes/nao-bounce/nao-bounce.plymouth
sudo update-initramfs -u
```

After restoring the previous theme, remove only the installed `nao-bounce` directory.
