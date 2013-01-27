from distutils.core import setup

setup(
    name='Cumuliform',
    version='0.1.0',
    author="Ross Delinger",
    author_email="rdelinger@helixoide.com",
    packages=['Cumuliform'],
    license='license.txt',
    description='Listen to the latest sound cloud tracks on hypem spy',
    long_description=open('README.txt').read(),
    install_requires=[
    "tornado",
    "beautifulsoup4",
    "soundcloud"],
    entry_points={
        'console_scripts': [
            'cumuliform = cumuliform:run',
            ],
        },
    )
