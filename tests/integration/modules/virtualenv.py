# -*- coding: utf-8 -*-

# Import python libs
import os
import tempfile

# Import Salt Testing libs
from salttesting.helpers import ensure_in_syspath
ensure_in_syspath('../../')

# Import salt libs
import integration


class VirtualenvModuleTest(integration.ModuleCase):
    '''
    Validate the virtualenv module
    '''
    def setUp(self):
        super(VirtualenvModuleTest, self).setUp()
        ret = self.run_function('cmd.has_exec', ['virtualenv'])
        if not ret:
            self.skipTest('virtualenv not installed')
        self.venv_test_dir = tempfile.mkdtemp(dir=integration.SYS_TMP_DIR)
        self.venv_dir = os.path.join(self.venv_test_dir, 'venv')

    def test_create_defaults(self):
        '''
        virtualenv.managed
        '''
        self.run_function('virtualenv.create', [self.venv_dir])
        pip_file = os.path.join(self.venv_dir, 'bin', 'pip')
        self.assertTrue(os.path.exists(pip_file))

    def test_site_packages(self):
        pip_bin = os.path.join(self.venv_dir, 'bin', 'pip')
        self.run_function(
            'virtualenv.create', [self.venv_dir], system_site_packages=True
        )
        with_site = self.run_function('pip.freeze', bin_env=pip_bin)
        self.run_function('file.remove', [self.venv_dir])
        self.run_function('virtualenv.create', [self.venv_dir])
        without_site = self.run_function('pip.freeze', bin_env=pip_bin)
        self.assertFalse(with_site == without_site)

    def test_clear(self):
        pip_bin = os.path.join(self.venv_dir, 'bin', 'pip')
        self.run_function('virtualenv.create', [self.venv_dir])
        self.run_function('pip.install', [], pkgs='pep8', bin_env=pip_bin)
        self.run_function('virtualenv.create', [self.venv_dir], clear=True)
        packages = self.run_function(
            'pip.list', prefix='pep8', bin_env=pip_bin
        )
        self.assertFalse('pep8' in packages)

    def tearDown(self):
        self.run_function('file.remove', [self.venv_test_dir])


if __name__ == '__main__':
    from integration import run_tests
    run_tests(VirtualenvModuleTest)
