#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Installation script for rst2md package '''
import os
from os.path import join as pjoin, split as psplit, splitext
import sys
import re

# For some commands, use setuptools.
if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb',
            'install_egg_info', 'egg_info', 'easy_install', 'bdist_wheel',
            'bdist_mpkg')).intersection(sys.argv)) > 0:
    import setuptools

from distutils.core import setup

# Get setuptools requirements from requirements.txt file
with open('requirements.txt', 'rt') as fobj:
    INSTALL_REQUIRES = [line.strip() for line in fobj if line.strip()]

# Requires for distutils (only used in pypi interface?)
_BREAK_VER = re.compile(r'(\S+?)(\[\S+\])?([=<>!]+\S+)')
REQUIRES = [_BREAK_VER.sub(r'\1 (\3)', req) for req in INSTALL_REQUIRES]

# Specific to setuptools execution
EXTRA_SETUP_KWARGS = ({} if 'setuptools' not in sys.modules
                      else {'install_requires': INSTALL_REQUIRES})

# See: https://github.com/matthew-brett/myscripter
from distutils.command.install_scripts import install_scripts
from distutils import log

BAT_TEMPLATE = \
r"""@echo off
REM wrapper to use shebang first line of {FNAME}
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call "%py_exe%" %pyscript% %*
"""

class my_install_scripts(install_scripts):
    """ Install .bat wrapper for scripts on Windows """
    def run(self):
        install_scripts.run(self)
        if not os.name == "nt":
            return
        for filepath in self.get_outputs():
            # If we can find an executable name in the #! top line of the
            # script file, make .bat wrapper for script.
            with open(filepath, 'rt') as fobj:
                first_line = fobj.readline()
            if not (first_line.startswith('#!') and
                    'python' in first_line.lower()):
                log.info("No #!python executable found, skipping .bat "
                            "wrapper")
                continue
            pth, fname = psplit(filepath)
            froot, ext = splitext(fname)
            bat_file = pjoin(pth, froot + '.bat')
            bat_contents = BAT_TEMPLATE.replace('{FNAME}', fname)
            log.info("Making %s wrapper for %s" % (bat_file, filepath))
            if self.dry_run:
                continue
            with open(bat_file, 'wt') as fobj:
                fobj.write(bat_contents)


CMDCLASS = dict(install_scripts = my_install_scripts)

_VERSION_RE = re.compile(r"""^__version__\s*=\s*['"](.*)['"]$""")
with open(pjoin('doctree2md', '__init__.py'), 'rt') as fobj:
    for line in fobj:
        match = _VERSION_RE.match(line)
        if match:
            VERSION = match.groups()[0]
            break


setup(name='rst2md',
      version=VERSION,
      cmdclass=CMDCLASS,
      description='Converting from ReST to markdown using docutils',
      author='Chris Wrench',
      author_email='c.g.wrench@gmail.com',
      maintainer='Chris Wrench',
      maintainer_email='c.g.wrench@gmail.com',
      url='http://github.com/cgwrench/rst2md',
      packages=['doctree2md',
                'doctree2md.tests'],
      package_data = {'doctree2md': [
          'tests/rst_md_files/*',
      ]},
      license='BSD license',
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Operating System :: MacOS',
        ],
      scripts = ['scripts/rst2md.py'],
      long_description = '',
      **EXTRA_SETUP_KWARGS
      )
