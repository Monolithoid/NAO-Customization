"""Exercise real GResource compilation and reversible changes in a temp tree."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('nao_install', Path(__file__).parents[1] / 'install.py')
nao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nao)


class ThemeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vendor = self.root / 'vendor.gresource'
        self.theme = self.root / 'gdm-theme.gresource'
        self.profile = self.root / 'profile/gdm'
        self.settings = self.root / 'db/gdm.d/99-nao-login'
        self.state = self.root / 'state'
        self.files = {
            'gnome-shell-dark.css': b'#lockDialogGroup { background-color: black; }',
            'gnome-shell-light.css': b'.login-dialog { color: black; }',
            'original.bin': bytes(range(256)),
        }
        self.make_resource(self.vendor, self.files)
        self.theme.symlink_to(self.vendor.name)
        self.original = self.vendor.read_bytes()
        for name, path in [('THEME', self.theme), ('PROFILE', self.profile),
                           ('SETTINGS', self.settings), ('STATE', self.state)]:
            context = patch.object(nao, name, path)
            context.start()
            self.addCleanup(context.stop)
        original_run = nao.run
        def runtime(*args):
            if args[0] == 'gnome-shell':
                return b'GNOME Shell 50.1\n'
            if args[0] == 'dconf':
                return b''  # No system database is touched by these tests.
            return original_run(*args)
        context = patch.object(nao, 'run', side_effect=runtime)
        context.start()
        self.addCleanup(context.stop)

    def make_resource(self, output, files):
        folder = self.root / ('source-' + output.stem)
        folder.mkdir()
        xml = ET.Element('gresources')
        resource = ET.SubElement(xml, 'gresource', prefix='/org/gnome/shell/theme')
        for name, data in files.items():
            (folder / name).write_bytes(data)
            ET.SubElement(resource, 'file').text = name
        manifest = folder / 'resource.xml'
        ET.ElementTree(xml).write(manifest)
        subprocess.check_call(['glib-compile-resources', str(manifest),
                               '--sourcedir', str(folder), '--target', str(output)])

    def test_build_preserves_assets_and_styles_both_variants(self):
        output = self.root / 'nao.gresource'
        nao.build(self.vendor, output, 1920, 1080, 1)
        for name in self.files:
            data = nao.run('gresource', 'extract', str(output),
                           '/org/gnome/shell/theme/' + name)
            if name.endswith('.css'):
                self.assertTrue(data.startswith(self.files[name]))
                self.assertIn(b'padding-right: 960.00px', data)
            else:
                self.assertEqual(data, self.files[name])
        image = nao.run('gresource', 'extract', str(output),
                        '/org/gnome/shell/theme/nao-login.png')
        self.assertEqual(image, (nao.HERE / 'assets/nao.png').read_bytes())
        self.assertEqual(self.original, self.vendor.read_bytes())

    def test_install_restore_preserves_vendor_symlink_and_profile(self):
        self.profile.parent.mkdir()
        self.profile.write_text('user-db:user\nsystem-db:site\n')
        nao.install(1920, 1080, 1)
        self.assertFalse(self.theme.is_symlink())
        self.assertEqual(self.vendor.read_bytes(), self.original)
        self.assertIn(b"logo=''", self.settings.read_bytes())
        self.assertIn(b'system-db:site', self.profile.read_bytes())
        self.assertIn(b'system-db:gdm', self.profile.read_bytes())
        nao.restore()
        self.assertTrue(self.theme.is_symlink())
        self.assertEqual(self.theme.readlink(), Path('vendor.gresource'))
        self.assertEqual(self.profile.read_text(), 'user-db:user\nsystem-db:site\n')
        self.assertFalse(self.settings.exists())
        self.assertFalse(self.state.exists())

    def test_regular_file_and_missing_profile_restore(self):
        self.theme.unlink()
        self.theme.write_bytes(self.original)
        self.theme.chmod(0o640)
        nao.install(1920, 1080, 1)
        nao.restore()
        self.assertEqual(self.theme.read_bytes(), self.original)
        self.assertEqual(self.theme.stat().st_mode & 0o777, 0o640)
        self.assertFalse(self.profile.exists())

    def test_restore_refuses_later_changes(self):
        nao.install(1920, 1080, 1)
        self.settings.write_text('administrator change')
        installed = self.theme.read_bytes()
        with self.assertRaisesRegex(ValueError, 'changed since installation'):
            nao.restore()
        self.assertEqual(self.theme.read_bytes(), installed)
        self.assertEqual(self.settings.read_text(), 'administrator change')
        self.assertTrue(self.state.exists())

    def test_failed_settings_update_rolls_back(self):
        saved_run = nao.run
        calls = 0
        def fail_once(*args):
            nonlocal calls
            if args[0] == 'dconf':
                calls += 1
                if calls == 1:
                    raise subprocess.CalledProcessError(1, args)
            return saved_run(*args)
        with patch.object(nao, 'run', side_effect=fail_once):
            with self.assertRaises(subprocess.CalledProcessError):
                nao.install(1920, 1080, 1)
        self.assertTrue(self.theme.is_symlink())
        self.assertEqual(self.vendor.read_bytes(), self.original)
        self.assertFalse(self.profile.exists())
        self.assertFalse(self.settings.exists())
        self.assertFalse(self.state.exists())

    def test_restore_retries_after_failed_database_update(self):
        nao.install(1920, 1080, 1)
        saved_run = nao.run
        calls = 0
        def fail_once(*args):
            nonlocal calls
            if args[0] == 'dconf':
                calls += 1
                if calls == 1:
                    raise subprocess.CalledProcessError(1, args)
            return saved_run(*args)
        with patch.object(nao, 'run', side_effect=fail_once):
            with self.assertRaises(subprocess.CalledProcessError):
                nao.restore()
            self.assertTrue(self.state.exists())
            self.assertTrue(self.theme.is_symlink())
            nao.restore()
        self.assertFalse(self.state.exists())
        self.assertEqual(self.theme.readlink(), Path('vendor.gresource'))
        self.assertFalse(self.profile.exists())
        self.assertFalse(self.settings.exists())

    def test_cli_installation_is_suspended(self):
        result = subprocess.run(['python3', str(nao.HERE / 'install.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Installation suspended', result.stderr)
        self.assertFalse(self.state.exists())

    def test_user_list_policy_is_not_overridden(self):
        self.assertNotIn(b'disable-user-list', nao.CONFIG)

    def test_unknown_resource_and_small_screen_are_rejected(self):
        source = self.root / 'unknown.gresource'
        self.make_resource(source, {'not-a-theme.css': b'body {}'})
        with self.assertRaisesRegex(ValueError, 'Unrecognized theme'):
            nao.build(source, self.root / 'out', 1920, 1080, 1)
        with self.assertRaisesRegex(ValueError, 'at least'):
            nao.build(self.vendor, self.root / 'out', 640, 480, 1)
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
