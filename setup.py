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
ProjecUrl="http://github.com/oisinmulvihill/evasion-web/tarball/pyramid-conversion#egg=evasion_web"
Version="1.1dev"
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='A web framework using Pyramids which helps you build Web Applications out of pluggable components.'
License='Evasion CDDL License.'
Description=Summary
ShortDescription=Summary

needed = [
    "Pyramid",
]


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
        'evasion.web-applet = evasion.web.pastercmds.evasionwebcmd:AppletTemplate',
    ],
}


setup(
    url=ProjecUrl,
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
    namespace_packages = ['evasion'],
)
