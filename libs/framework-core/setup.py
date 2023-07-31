# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack


import os
import re
import sys
import subprocess
import shutil

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import setuptools

PLUGIN_NAME = 'ftrack-framework-core-{0}'

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

SOURCE_PATH = os.path.join(ROOT_PATH, 'source')

README_PATH = os.path.join(ROOT_PATH, 'README.md')

RESOURCE_PATH = os.path.join(ROOT_PATH, 'resource')

HOOK_PATH = os.path.join(ROOT_PATH, 'hook')

BUILD_PATH = os.path.join(ROOT_PATH, 'build')


def get_version():
    '''Read version from _version.py, updated by CI based on monorepo package tag'''
    version_path = os.path.join(
        SOURCE_PATH, 'ftrack_framework_core', '_version.py'
    )
    with open(version_path, 'r') as file_handle:
        for line in file_handle.readlines():
            if line.find('__version__') > -1:
                return re.findall(r'\'(.*)\'', line)[0].strip()
    raise ValueError('Could not find version in {0}'.format(version_path))


VERSION = get_version()

STAGING_PATH = os.path.join(BUILD_PATH, PLUGIN_NAME.format(VERSION))


class BuildPlugin(setuptools.Command):
    '''Build plugin.'''

    description = 'Download dependencies and build plugin .'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Run the build step.'''
        # Clean staging path
        shutil.rmtree(STAGING_PATH, ignore_errors=True)

        # Copy resource files
        shutil.copytree(RESOURCE_PATH, os.path.join(STAGING_PATH, 'resource'))

        # Copy plugin files
        shutil.copytree(HOOK_PATH, os.path.join(STAGING_PATH, 'hook'))
        dependencies_path = os.path.join(STAGING_PATH, 'dependencies')

        os.makedirs(dependencies_path)

        subprocess.check_call(
            [
                sys.executable,
                '-m',
                'pip',
                'install',
                '.',
                '--target',
                dependencies_path,
            ]
        )

        result_path = shutil.make_archive(
            STAGING_PATH,
            'zip',
            STAGING_PATH,
        )


# Custom commands.
class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest

        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


# Configuration.
setup(
    name='ftrack-framework-core',
    description='ftrack core pipeline integration framework.',
    long_description=open(README_PATH).read(),
    keywords='ftrack',
    url='https://github.com/ftrackhq/integrations/libs/framework-core',
    author='ftrack',
    author_email='support@ftrack.com',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={'': 'source'},
    package_data={
        "": ["{}/**/*.*".format(RESOURCE_PATH), "{}/**/*.py".format(HOOK_PATH)]
    },
    version=VERSION,
    python_requires='<3.10',
    setup_requires=[
        'sphinx >= 1.8.5, < 6',
        'sphinx_rtd_theme >= 0.1.6, < 2',
        'lowdown >= 0.1.0, < 2',
        'setuptools>=44.0.0',
        'setuptools_scm',
        'Jinja2<3.2',
    ],
    install_requires=[
        'ftrack-python-api >= 1, < 3',  # == 2.0RC1
        'future >=0.16.0, < 1',
        'six >= 1, < 2',
        'jsonschema==2.6.0',
        'appdirs',
        'python_jsonschema_objects <= 0.3.12',
        'jsonref',
        'markdown<=3.2.2',
        # Keep importlib-metadata it low, otherwise python_jsonschema_objects
        # build on python 3.7.12 will not work on maya 2022
        'importlib-metadata<5.0',
    ],
    tests_require=['mock', 'pytest >= 2.3.5, < 3'],
    cmdclass={'test': PyTest, 'build_plugin': BuildPlugin},
    zip_safe=False,
)