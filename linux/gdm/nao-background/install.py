#!/usr/bin/env python3
"""Configure native Ubuntu GDM background or colors; preserve the greeter profile."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PROFILE_PATHS = (Path('/etc/dconf/profile/gdm'), Path('/usr/share/dconf/profile/gdm'))
GENERATOR = Path('/usr/share/gdm/generate-config')
SOURCE_DIR = Path('/usr/share/gdm/dconf')
DROPIN = SOURCE_DIR / '99-nao-background'
ASSET = Path('/usr/local/share/nao-gdm-background/nao-background.svg')
STATE = Path('/var/lib/nao-gdm-background')
OLD_STATE = Path('/var/lib/nao-gdm')
COLOR_DROPIN = SOURCE_DIR / '99-nao-colors'
COLOR_STATE = Path('/var/lib/nao-gdm-colors')
COLORS = b"[org/gnome/desktop/interface]\ncolor-scheme='prefer-dark'\naccent-color='blue'\n"


def run(*args):
    return subprocess.check_output(args)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.nao-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            os.fchmod(output.fileno(), mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def settings():
    return ("[com/ubuntu/login-screen]\n"
            f"background-picture-uri='{ASSET.as_uri()}'\n"
            "background-size='cover'\n"
            "background-repeat='no-repeat'\n").encode()


def check():
    if OLD_STATE.exists():
        raise ValueError('Restore the suspended full theme first: linux/gdm/nao/install.py --restore')
    profile = next((p for p in PROFILE_PATHS if p.exists()), None)
    if profile is None or 'file-db:/var/lib/gdm3/greeter-dconf-defaults' not in profile.read_text().splitlines():
        raise ValueError('Unexpected active GDM profile; no changes made. Keep the original profile intact.')
    if not GENERATOR.is_file() or not os.access(GENERATOR, os.X_OK) or not SOURCE_DIR.is_dir():
        raise ValueError('Ubuntu GDM configuration generator or source directory is missing')
    for key in ('background-picture-uri', 'background-size', 'background-repeat'):
        run('gsettings', 'range', 'com.ubuntu.login-screen', key)


def install():
    check()
    if any(p.exists() or p.is_symlink() for p in (STATE, DROPIN, ASSET)):
        raise ValueError('NAO background files already exist. Restore before installing again.')
    changes = [(ASSET, (HERE / 'nao-background.svg').read_bytes()), (DROPIN, settings())]
    STATE.mkdir(mode=0o700, parents=True)
    records = [{'path': str(path), 'sha256': digest(data)} for path, data in changes]
    write(STATE / 'files.json', json.dumps(records).encode(), 0o600)
    created = []
    try:
        for path, data in changes:
            write(path, data)
            created.append(path)
        run(str(GENERATOR))
    except BaseException:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        # Rebuild the original database; retain recovery state if this fails too.
        run(str(GENERATOR))
        shutil.rmtree(STATE)
        raise
    print('Native GDM background configured. Save your work, then log out or reboot to inspect it.')
    print('The GDM service was not restarted; the greeter profile and theme were not modified.')


def restore():
    records = json.loads((STATE / 'files.json').read_text())
    expected = {str(ASSET), str(DROPIN)}
    if len(records) != 2 or {r['path'] for r in records} != expected:
        raise ValueError('Unexpected recovery record; no files removed')
    for record in records:
        path = Path(record['path'])
        if path.is_symlink() or (path.exists() and digest(path.read_bytes()) != record['sha256']):
            raise ValueError(f'{path} changed after installation; recovery state retained')
    for record in reversed(records):
        Path(record['path']).unlink(missing_ok=True)
    run(str(GENERATOR))
    shutil.rmtree(STATE)
    print('NAO background override removed; previous GDM defaults regenerated. GDM was not restarted.')


def install_colors():
    check()
    # Validate the chosen native values, not just the presence of the keys.
    for key, value in [('color-scheme', 'prefer-dark'), ('accent-color', 'blue')]:
        values = run('gsettings', 'range', 'org.gnome.desktop.interface', key).decode()
        if f"'{value}'" not in values.splitlines():
            raise ValueError(f'Native {key} does not support {value}; no changes made')
    if any(p.exists() or p.is_symlink() for p in (COLOR_STATE, COLOR_DROPIN)):
        raise ValueError('NAO colors already exist. Use --restore-colors before reinstalling.')
    COLOR_STATE.mkdir(mode=0o700, parents=True)
    write(COLOR_STATE / 'files.json', json.dumps([
        {'path': str(COLOR_DROPIN), 'sha256': digest(COLORS)}
    ]).encode(), 0o600)
    try:
        write(COLOR_DROPIN, COLORS)
        run(str(GENERATOR))
    except BaseException:
        COLOR_DROPIN.unlink(missing_ok=True)
        run(str(GENERATOR))
        shutil.rmtree(COLOR_STATE)
        raise
    print('Native dark preference and blue accent configured for the GDM greeter.')
    print('Save your work, then log out to inspect. The background was not changed.')


def restore_colors():
    records = json.loads((COLOR_STATE / 'files.json').read_text())
    if len(records) != 1 or records[0]['path'] != str(COLOR_DROPIN):
        raise ValueError('Unexpected color recovery record; no files removed')
    if COLOR_DROPIN.is_symlink() or (COLOR_DROPIN.exists() and
            digest(COLOR_DROPIN.read_bytes()) != records[0]['sha256']):
        raise ValueError(f'{COLOR_DROPIN} changed after installation; recovery state retained')
    COLOR_DROPIN.unlink(missing_ok=True)
    run(str(GENERATOR))
    shutil.rmtree(COLOR_STATE)
    print('NAO color override removed. Existing background configuration was preserved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--restore', action='store_true', help='Restore only the background')
    mode.add_argument('--colors', action='store_true', help='Use native dark preference and blue accent')
    mode.add_argument('--restore-colors', action='store_true', help='Restore only the colors')
    args = parser.parse_args()
    try:
        if os.geteuid() != 0:
            raise ValueError('Run with sudo')
        if args.colors:
            install_colors()
        elif args.restore_colors:
            restore_colors()
        elif args.restore:
            restore()
        else:
            install()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
