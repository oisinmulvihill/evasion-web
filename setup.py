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

Name='evasion-webadmin'
ProjecUrl="" #""
Version='1.0.0'
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='Local/Remote web admin application for director and its running processes.'
License=''
ShortDescription=Summary
Description=Summary

needed = [
        "Pylons>=0.9.7",
        "repoze.tm2 >= 1.0a4",        
        "repoze.what",
        "repoze.what-pylons",
        "repoze.what.plugins.ini>=0.2.2",
        "repoze.who-friendlyform>=1.0b2",
        "fcrypt",
        "tailer",
        "evasion-messenger",
        "evasion-director",
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
    'webadmin',
]

ProjectScripts = [
    'scripts/runwebadmin',
]

PackageData = {
    '': ['*.*'],
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
    setup_requires=["PasteScript>=1.6.3"],
    paster_plugins=['PasteScript', 'Pylons'],
    #package_data={'webadmin': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'webadmin': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    #entry_points="""
    #[paste.app_factory]
    #main = webadmin.config.middleware:make_app
    #
    #[paste.app_install]
    #main = pylons.util:PylonsInstaller
    #""",
)

