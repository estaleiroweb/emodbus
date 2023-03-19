import subprocess
import sys
import os
import shutil
from setuptools import setup, find_packages


def getVersion() -> str:
    assert os.path.isfile(f'version.py')
    try:
        lpros = ['git', 'describe', '--tags']
        sb = subprocess.run(lpros, stdout=subprocess.PIPE)
        ver = sb.stdout.decode('utf-8').strip()
    except:
        ver = ''
    if ver == '':
        with open(f'VERSION', 'r', encoding='utf-8') as fh:
            ver = fh.read().strip()
    if ver == '':
        ver = '0.0.1'
    if '-' in ver:
        # when not on tag, git describe outputs: '1.3.3-22-gdf81228'
        # pip has gotten strict with version numbers
        # so change it to: '1.3.3+22.git.gdf81228'
        # See: https://peps.python.org/pep-0440/#local-version-segments
        v, i, s = ver.split('-')
        ver = v.replace('v', '')

    assert '-' not in ver
    assert '.' in ver
    with open(f'VERSION', 'w', encoding='utf-8') as fh:
        fh.write('%s\n' % ver)
    return ver


def getPackages() -> list:
    packages = []
    for dirname, dirnames, filenames in os.walk(rootdir):
        if dirname != rootdir and '__init__.py' in filenames:
            packages.append(os.path.basename(dirname))
    return packages


def getRequirements() -> list[str]:
    with open(f'{rootdir}/requirement.txt', 'r') as file:
        return [line.strip() for line in file]


def getReadme() -> str:
    with open(f'{rootdir}/README.md', 'r', encoding='utf-8') as fh:
        return fh.read()


def getLicence() -> str:
    with open(f'{rootdir}/LICENCE', 'r', encoding='utf-8') as fh:
        return fh.readline().lstrip().rstrip()


rootdir = os.path.abspath(__file__ + '/..')
os.chdir(rootdir)
try:
    shutil.rmtree(rootdir+'/dist',)
except:
    ...
try:
    shutil.rmtree(rootdir+'/build',)
except:
    ...
try:
    shutil.rmtree(rootdir+'/magic_methods.egg-info',)
except:
    ...

projectName = os.path.basename(rootdir)

# projectPath = projectName.replace('-', '')
licence = getLicence()
dictSetup = {
    'name': projectName,
    'version': getVersion(),
    'license': licence,
    'author': 'Helbert Braga Fernandes',
    'author_email': 'helbertfernandes@gmail.com',
    'description': u'All Magic Methods Implement. You can easyly to implement all magic methods or part of them',
    'long_description': getReadme(),
    'long_description_content_type': 'text/markdown',
    'url': 'https://github.com/estaleiroweb/mandrake',
    'include_package_data': True,
    'keywords': 'magic methods class',
    'classifiers': [  # https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        f'License :: OSI Approved :: {licence}',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    'python_requires': '>=2.0',
    'install_requires': getRequirements() + [
        # 'dataclasses==0.7;python_version<3.8',
        # 'requests >= 2.25.1',
        # 'apache-libcloud >= 3.3.1',
    ],
    'packages': find_packages(),
    # 'packages': getPackages(),
    # 'package_data': {projectPath: ['VERSION']},
    # 'package_dir': {'magicmethods':'./magicmethods'},
    # 'entry_points':{'console_scripts': [f'{projectPath} = {projectPath}.main:main']},
}
if len(sys.argv) < 2:
    sys.argv.append('bdist_wheel')
setup(**dictSetup)
