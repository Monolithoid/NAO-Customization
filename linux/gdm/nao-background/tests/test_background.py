"""Compile real dconf databases in an isolated tree; never touch a live greeter."""
import importlib.util
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('background', Path(__file__).parents[1] / 'install.py')
bg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg)


class BackgroundTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sources = self.root / 'dconf'
        self.sources.mkdir()
        self.original = (self.sources / '00-upstream-settings')
        self.original.write_text("[org/gnome/desktop/session]\nsession-name='gnome-login'\n"
                                 "[org/gnome/desktop/lockdown]\ndisable-user-switching=true\n")
        self.profile = self.root / 'vendor-profile'
        self.profile.write_text('user-db:user\nfile-db:/var/lib/gdm3/greeter-dconf-defaults\n')
        self.profile_before = self.profile.read_bytes()
        self.compiled = self.root / 'database'
        self.read_profile = self.root / 'read-profile'
        self.read_profile.write_text(f'file-db:{self.compiled}\n')
        self.generator = self.root / 'generate-config'
        self.generator.write_text('#!/bin/sh\nset -e\ndconf compile ' +
                                  shlex.quote(str(self.compiled)) + ' ' +
                                  shlex.quote(str(self.sources)) + '\n')
        self.generator.chmod(0o755)
        replacements = {
            'PROFILE_PATHS': (self.root / 'etc-profile', self.profile),
            'GENERATOR': self.generator, 'SOURCE_DIR': self.sources,
            'DROPIN': self.sources / '99-nao-background',
            'ASSET': self.root / 'assets/nao-background.svg',
            'STATE': self.root / 'state', 'OLD_STATE': self.root / 'old-state',
        }
        for key, value in replacements.items():
            context = patch.object(bg, key, value)
            context.start()
            self.addCleanup(context.stop)
        # Native Ubuntu schemas are not installed on the Debian test host.
        real_run = bg.run
        def command(*args):
            if args[0] == 'gsettings':
                self.assertEqual(args[1:3], ('range', 'com.ubuntu.login-screen'))
                self.assertIn(args[3], ('background-picture-uri', 'background-size', 'background-repeat'))
                return b'type s\n'
            return real_run(*args)
        context = patch.object(bg, 'run', side_effect=command)
        context.start()
        self.addCleanup(context.stop)
        self.env = dict(os.environ, DCONF_PROFILE=str(self.read_profile))

    def read(self, key):
        return subprocess.check_output(['dconf', 'read', key], env=self.env).decode().strip()

    def test_native_settings_preserve_session_and_profile_and_restore(self):
        bg.run(str(self.generator))
        original_dump = subprocess.check_output(['dconf', 'dump', '/'], env=self.env)
        bg.install()
        self.assertEqual(self.read('/org/gnome/desktop/session/session-name'), "'gnome-login'")
        self.assertEqual(self.read('/org/gnome/desktop/lockdown/disable-user-switching'), 'true')
        self.assertEqual(self.read('/com/ubuntu/login-screen/background-picture-uri'),
                         "'" + bg.ASSET.as_uri() + "'")
        self.assertEqual(self.read('/com/ubuntu/login-screen/background-size'), "'cover'")
        self.assertEqual(self.profile.read_bytes(), self.profile_before)
        self.assertFalse(bg.PROFILE_PATHS[0].exists())
        self.assertEqual(set(bg.settings().decode().splitlines()[1:]), {
            f"background-picture-uri='{bg.ASSET.as_uri()}'",
            "background-size='cover'", "background-repeat='no-repeat'"})
        bg.restore()
        self.assertEqual(subprocess.check_output(['dconf', 'dump', '/'], env=self.env), original_dump)
        self.assertEqual(self.profile.read_bytes(), self.profile_before)
        self.assertFalse(bg.STATE.exists())
        self.assertFalse(bg.ASSET.exists())

    def test_old_custom_profile_is_rejected_without_modification(self):
        bg.PROFILE_PATHS[0].write_text('user-db:user\nsystem-db:gdm\n')
        with self.assertRaisesRegex(ValueError, 'Unexpected active GDM profile'):
            bg.install()
        self.assertFalse(bg.STATE.exists())
        self.assertFalse(bg.DROPIN.exists())
        self.assertEqual(self.profile.read_bytes(), self.profile_before)

    def test_previous_experimental_install_must_be_restored(self):
        bg.OLD_STATE.mkdir()
        with self.assertRaisesRegex(ValueError, 'Restore the suspended full theme'):
            bg.install()
        self.assertFalse(bg.STATE.exists())

    def test_later_changes_are_not_deleted(self):
        bg.install()
        bg.DROPIN.write_text('administrator changes\n')
        with self.assertRaisesRegex(ValueError, 'changed after installation'):
            bg.restore()
        self.assertTrue(bg.ASSET.exists())
        self.assertTrue(bg.STATE.exists())

    def test_generator_failure_rolls_back_added_files(self):
        original_run = bg.run
        failed = False
        def fail_once(*args):
            nonlocal failed
            if args[0] == str(bg.GENERATOR) and not failed:
                failed = True
                raise subprocess.CalledProcessError(1, args)
            return original_run(*args)
        with patch.object(bg, 'run', side_effect=fail_once):
            with self.assertRaises(subprocess.CalledProcessError):
                bg.install()
        self.assertFalse(bg.ASSET.exists())
        self.assertFalse(bg.DROPIN.exists())
        self.assertFalse(bg.STATE.exists())
        self.assertEqual(self.profile.read_bytes(), self.profile_before)
        self.assertEqual(self.read('/org/gnome/desktop/session/session-name'), "'gnome-login'")


if __name__ == '__main__':
    unittest.main()
