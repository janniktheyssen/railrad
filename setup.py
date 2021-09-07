try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Railway track radiation using pre-calculated transfer functions',
    'author': 'Jannik Theyssen',
    'url': 'www.github.com/janniktheyssen/railrad',
    'download_url': 'https://github.com/janniktheyssen/railrad',
    'author_email': 'jannik.theyssen@gmail.com',
    'version': '0.1',
    'install_requires': ['numpy>=1.19.5', 'scipy', 'h5py'],
    'packages': ['railrad'],
    'scripts': [],
    'name': 'RailRad',
}

setup(**config)
