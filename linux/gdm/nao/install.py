#!/usr/bin/env python3
"""Build, install, or restore the NAO GDM theme (GNOME Shell 50.x)."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
THEME = Path('/usr/share/gnome-shell/gdm-theme.gresource')
PROFILE = Path('/etc/dconf/profile/gdm')
SETTINGS = Path('/etc/dconf/db/gdm.d/99-nao-login')
STATE = Path('/var/lib/nao-gdm')
CONFIG = b"[org/gnome/login-screen]\nlogo=''\ndisable-user-list=false\n"


def run(*args):
    return subprocess.check_output(args)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data, mode=0o644):
    """Replace the named entry, never follow an existing theme symlink."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.nao-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            os.fchmod(output.fileno(), mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def snapshot(path):
    if path.is_symlink():
        return {'kind': 'symlink', 'target': os.readlink(path)}
    if path.exists():
        return {'kind': 'file', 'data': path.read_bytes().hex(),
                'mode': path.stat().st_mode & 0o777}
    return {'kind': 'absent'}


def recover(path, saved):
    if saved['kind'] == 'file':
        atomic_write(path, bytes.fromhex(saved['data']), saved['mode'])
    elif saved['kind'] == 'symlink':
        # The original target may have been upgraded; preserve the original link.
        temporary = path.with_name('.' + path.name + '.nao-restore')
        temporary.unlink(missing_ok=True)
        temporary.symlink_to(saved['target'])
        os.replace(temporary, path)
    else:
        path.unlink(missing_ok=True)


def build(source, output, width, height, scale):
    if not source.is_file():
        raise ValueError(f'Theme resource not found: {source}')
    if width < 1280 or height < 720 or not 1 <= scale <= 3:
        raise ValueError('Use at least 1280x720 physical pixels and a scale from 1 to 3')
    w, h = width / scale, height / scale
    if w < 960 or h < 540:
        raise ValueError('This two-column layout needs at least 960x540 logical pixels')
    names = run('gresource', 'list', str(source)).decode().splitlines()
    styles = [n for n in names if n.endswith('.css')]
    if not styles or not any(PurePosixPath(n).name in {
            'gnome-shell.css', 'gnome-shell-dark.css', 'gnome-shell-light.css', 'gdm.css'
    } for n in styles):
        raise ValueError('Unrecognized theme: no GNOME Shell stylesheet. Original theme unchanged.')
    with tempfile.TemporaryDirectory(prefix='nao-gdm-') as temporary:
        root = Path(temporary)
        xml = ET.Element('gresources')
        resource = ET.SubElement(xml, 'gresource', prefix='/')
        for name in names:
            relative = PurePosixPath(name.lstrip('/'))
            if '..' in relative.parts:
                raise ValueError('Unsafe resource path')
            data = run('gresource', 'extract', str(source), name)
            if name.endswith('.css'):
                # Override every color variant so the chosen greeter variant matches.
                data += css(w, h).encode()
            target = root / str(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            ET.SubElement(resource, 'file').text = str(relative)
        mascot = root / 'org/gnome/shell/theme/nao-login.png'
        if mascot.exists():
            raise ValueError('Resource already contains NAO assets; restore before reinstalling')
        mascot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / 'assets/nao.png', mascot)
        ET.SubElement(resource, 'file').text = 'org/gnome/shell/theme/nao-login.png'
        manifest = root / 'theme.xml'
        ET.ElementTree(xml).write(manifest, encoding='utf-8', xml_declaration=True)
        run('glib-compile-resources', str(manifest), '--sourcedir', str(root),
            '--target', str(output))
        result = run('gresource', 'list', str(output)).decode().splitlines()
        if set(result) != set(names) | {'/org/gnome/shell/theme/nao-login.png'}:
            raise ValueError('Compiled resource failed verification')


def css(w, h):
    # St CSS does not support percentage padding. Match the primary monitor's
    # logical geometry instead; the content box centers both selection and prompt.
    mascot_h = h * 0.80
    mascot_w = mascot_h * 300 / 360
    return f'''
/* NAO login theme: generated for {w:g}x{h:g} logical pixels. */
#lockDialogGroup {{
  background-color: #090e1a;
  background-gradient-direction: vertical;
  background-gradient-start: #090e1a;
  background-gradient-end: #121f33;
  background-image: url("resource:///org/gnome/shell/theme/nao-login.png");
  background-repeat: no-repeat;
  background-size: {mascot_w:.2f}px {mascot_h:.2f}px;
  background-position: {w * .75 - mascot_w / 2:.2f}px {h * .10:.2f}px;
}}
.login-dialog {{ color: #e6f2ff; padding-right: {w / 2:.2f}px; }}
.login-dialog-user-list-item {{
  color: #e6f2ff; background-color: #192b42;
  border: 1px solid #314861; border-radius: 12px;
}}
.login-dialog-user-list-item:hover,
.login-dialog-user-list-item:focus,
.login-dialog-user-list-item:selected {{
  color: #e6f2ff; background-color: #213c55; border-color: #46d4ec;
}}
.login-dialog StEntry {{ color: #e6f2ff; background-color: #192b42; }}
.login-dialog StEntry:focus {{ border-color: #46d4ec; }}
.login-dialog .button {{ color: #e6f2ff; background-color: #213c55; }}
.login-dialog .button:focus {{ border-color: #46d4ec; }}
'''


def install(width, height, scale):
    if STATE.exists():
        raise ValueError(f'Existing installation or backup at {STATE}. Restore before reinstalling.')
    version = run('gnome-shell', '--version').decode().strip()
    if not version.startswith('GNOME Shell 50.'):
        raise ValueError(f'Expected GNOME Shell 50.x, found: {version}')
    if SETTINGS.exists() or SETTINGS.is_symlink():
        raise ValueError(f'Refusing to overwrite existing settings: {SETTINGS}')
    # Keep symlinked administrator profiles untouched.
    if PROFILE.is_symlink():
        raise ValueError('Custom symlinked GDM profile detected; manual configuration required')
    profile = PROFILE.read_bytes() if PROFILE.exists() else b'user-db:user\n'
    lines = [line.strip() for line in profile.decode().splitlines()]
    if 'system-db:gdm' not in lines:
        profile = profile.rstrip(b'\n') + b'\nsystem-db:gdm\n'
    with tempfile.TemporaryDirectory(prefix='nao-gdm-install-') as temporary:
        output = Path(temporary) / 'theme.gresource'
        build(THEME, output, width, height, scale)
        changes = [(THEME, output.read_bytes()), (PROFILE, profile), (SETTINGS, CONFIG)]
        records = [{'path': str(path), 'before': snapshot(path),
                    'installed_sha256': digest(data)} for path, data in changes]
        STATE.mkdir(mode=0o700, parents=True)
        atomic_write(STATE / 'backup.json', json.dumps(records).encode(), 0o600)
        changed = []
        try:
            for (path, data), record in zip(changes, records):
                atomic_write(path, data)
                changed.append(record)
            run('dconf', 'update')
        except BaseException:
            for record in reversed(changed):
                recover(Path(record['path']), record['before'])
            # Keep the backup if the settings database cannot be rebuilt.
            run('dconf', 'update')
            shutil.rmtree(STATE)
            raise
    print('NAO GDM theme installed. Save your work, then log out to inspect it.')
    print('GDM was not restarted. Restore with: sudo python3 install.py --restore')


def restore():
    backup = STATE / 'backup.json'
    records = json.loads(backup.read_text())
    # Check all entries before restoring any; do not clobber later user changes.
    for record in records:
        path = Path(record['path'])
        if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != record['installed_sha256']:
            raise ValueError(f'{path} changed since installation. Backup kept at {backup}; restore manually.')
    for record in reversed(records):
        recover(Path(record['path']), record['before'])
    run('dconf', 'update')
    shutil.rmtree(STATE)
    print('Original GDM theme and profile restored. GDM was not restarted.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--width', type=int, default=1920, help='Primary monitor physical width')
    parser.add_argument('--height', type=int, default=1080, help='Primary monitor physical height')
    parser.add_argument('--scale', type=float, default=1, help='GDM display scale (default: 1)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--restore', action='store_true')
    group.add_argument('--output', type=Path, help='Build only; do not install (no root needed)')
    parser.add_argument('--source', type=Path, default=THEME, help='Resource for build-only mode')
    args = parser.parse_args()
    try:
        required = (['dconf'] if args.restore else
                    ['gresource', 'glib-compile-resources'] if args.output else
                    ['gresource', 'glib-compile-resources', 'dconf', 'gnome-shell'])
        for tool in required:
            if not shutil.which(tool):
                raise ValueError(f'Missing command: {tool}. See README prerequisites.')
        if args.output:
            if args.output.resolve() == args.source.resolve():
                raise ValueError('Build output must differ from source')
            build(args.source, args.output, args.width, args.height, args.scale)
            print(f'Built {args.output}; no system settings changed.')
        else:
            if os.geteuid() != 0:
                raise ValueError('Installation/restoration requires sudo')
            if args.restore:
                restore()
            else:
                install(args.width, args.height, args.scale)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
