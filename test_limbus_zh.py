import hashlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

loader = importlib.machinery.SourceFileLoader('limbus_zh', str(Path(__file__).with_name('limbus-zh')))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)


class InstallerTests(unittest.TestCase):
    def test_extra_library_with_spaces(self):
        with tempfile.TemporaryDirectory() as t:
            home = Path(t)
            root = home / '.local/share/Steam'
            (root / 'steamapps').mkdir(parents=True)
            library = home / 'external disk'
            game = library / 'steamapps/common/Limbus Company'
            game.mkdir(parents=True)
            (game / 'LimbusCompany.exe').touch()
            (library / 'steamapps/appmanifest_1973530.acf').write_text('"AppState" {"installdir" "Limbus Company"}')
            (root / 'steamapps/libraryfolders.vdf').write_text('"libraryfolders" {"1" {"path" "' + str(library) + '"}}')
            self.assertEqual(m.discover(home), [game.resolve()])

    def test_zip_traversal_and_links(self):
        with tempfile.TemporaryDirectory() as t:
            archive = Path(t) / 'bad.zip'
            for name in ['../../outside', '/tmp/outside', str(m.REL) + '/../../outside']:
                with zipfile.ZipFile(archive, 'w') as z:
                    z.writestr(name, 'bad')
                with self.assertRaises(ValueError):
                    m.extract_text(archive, Path(t) / 'stage')
            with zipfile.ZipFile(archive, 'w') as z:
                info = zipfile.ZipInfo(str(m.REL) + '/link')
                info.external_attr = 0o120777 << 16
                z.writestr(info, '/tmp')
            with self.assertRaises(ValueError):
                m.extract_text(archive, Path(t) / 'stage')

    def test_failed_deploy_restores_previous(self):
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / 'live'
            target.mkdir()
            (target / 'old').touch()
            with self.assertRaises(FileNotFoundError):
                m.deploy(target, Path(t) / 'missing', Path(t) / 'backup')
            self.assertTrue((target / 'old').exists())

    def test_parent_symlink_refused(self):
        with tempfile.TemporaryDirectory() as t:
            alias = Path(t) / 'alias'
            alias.symlink_to(t)
            with self.assertRaises(ValueError):
                m.guard(alias / 'Lang')

    def test_real_packages(self):
        # Optional integration fixture supplied through LLC_FIXTURES.
        fixtures = os.environ.get('LLC_FIXTURES')
        if not fixtures:
            self.skipTest('LLC_FIXTURES not set')
        fixtures = Path(fixtures)
        release = json.loads((fixtures / 'release.json').read_text())
        tree = json.loads((fixtures / 'tree.json').read_text())
        font_sha = next(x['sha'] for x in tree['tree'] if x['path'] == 'Fonts/LLCCN-Font.7z')
        font_meta = {'sha': font_sha, 'download_url': 'font'}
        def get_meta(url):
            return font_meta if '/contents/' in url else release
        def local_download(url, dest, expected, git_blob=False):
            source = fixtures / ('font.7z' if git_blob else 'text.zip')
            data = source.read_bytes()
            digest = hashlib.sha1(('blob %d\0' % len(data)).encode() + data).hexdigest() if git_blob else hashlib.sha256(data).hexdigest()
            self.assertEqual(digest, expected)
            dest.write_bytes(data)
        with tempfile.TemporaryDirectory() as t:
            game = Path(t)
            (game / 'LimbusCompany.exe').touch()
            (game / 'LimbusCompany_Data').mkdir()
            with patch.object(m, 'metadata', side_effect=get_meta), patch.object(m, 'download', side_effect=local_download), patch.object(m, 'running', return_value=False):
                m.main(['install', '--game-dir', t])
                target = game / m.REL
                self.assertTrue((target / 'Font/Context/ChineseFont.ttf').is_file())
                self.assertTrue((target / 'Info/LICENSE').is_file())
                self.assertEqual(m.read_state(target)['version'], release['tag_name'])
                (target / 'user-marker').write_text('old')
                m.main(['update', '--force', '--game-dir', t])
                self.assertFalse((target / 'user-marker').exists())
                m.main(['rollback', '--game-dir', t])
                self.assertEqual((target / 'user-marker').read_text(), 'old')
                m.main(['update', '--force', '--discard-backup', '--game-dir', t])
                self.assertFalse((target / 'user-marker').exists())


if __name__ == '__main__':
    unittest.main()
