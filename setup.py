"""
Project's setuptool configuration.

This should eggify and in theory upload to pypi without problems.

Oisin Mulvihill
2010-02-25

"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

Name='evasion-web'
ProjecUrl="http://github.com/oisinmulvihill/evasion-web/tarball/master#egg=evasion_web"
Version="1.2dev"
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='A web framework using Pyramids which helps you build Web Applications out of pluggable components.'
License=''
ShortDescription=Summary
Description=r"""A

"""

needed = [
        "Pylons==0.9.7",
        "Paste",
        "PasteScript",
        "repoze.tm2 >= 1.0a4",
        "repoze.who == 1.0.18",
        "repoze.what",
        "repoze.what-pylons",
        "repoze.what.plugins.ini>=0.2.2",
        "repoze.who-friendlyform>=1.0b2",
        "fcrypt",
]


# Include everything under viewpoint. I needed to add a __init__.py
# to each directory inside viewpoint. I did this using the following
# handy command:
#
#  find webadmin -type d -exec touch {}//__init__.py \;
#
# If new directories are added then I'll need to rerun this command.
#
EagerResources = [
    'evasion',
]

ProjectScripts = [
    'scripts/runweb',
]

PackageData = {
    '': ['*.*'],
}

# Make executable versions of the scripts:
EntryPoints = {
    'console_scripts': [
        'runweb = evasion.web.scripts.main:main',
    ],

    'paste.paster_create_template' : [
        'evasion.web-project = evasion.web.pastercmds.evasionwebcmd:ProjectTemplate',
        'evasion.web-app = evasion.web.pastercmds.evasionwebcmd:AppTemplate',
    ],

    'paste.paster_command' : [
#        'ev-newapp = evasion.web.pastercmds.evasionwebcmd:CreateAppCmd',
    ]
}


setup(
#    url=ProjecUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    include_package_data=True,
    packages=find_packages(),
    package_data=PackageData,
    eager_resources = EagerResources,
    entry_points = EntryPoints,
    setup_requires=["PasteScript>=1.6.3"],
    paster_plugins=['PasteScript', 'Pylons'],
    namespace_packages = ['evasion'],
)
