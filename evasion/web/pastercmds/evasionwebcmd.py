"""
This provides the set up need to provide EvasionWeb specific
commands in paster. This module provides customer Project and
App template creation as well as other useful commands.

Oisin Mulvihill
2010-08-03

"""
# http://pythonpaste.org/script/developer.html
#
from paste.script.command import Command
from paste.script.templates import Template, var

vars = [
    var('version', 'Version (like 0.1)', default='0.1'),
    var('description', 'One-line description of the package'),
    var('long_description', 'Multi-line description (in reST)'),
    var('keywords', 'Space-separated keywords/tags'),
    var('author', 'Author name'),
    var('author_email', 'Author email'),
    var('url', 'URL of homepage'),
    var('license_name', 'License name', 'Commercial, All rights reserved.'),
    var('zip_safe', 'True/False: if the package can be distributed as a .zip file', default=False),
]

class ProjectTemplate(Template):
    """Set up to create an EvasionWeb project.
    
    This is simply a configuration file, some
    basic user/group/permission auth setup and
    an empty package.
    
    runweb is run from this folder to pickup
    development.ini and the App plugins to 
    load.
    
    """
    _template_dir = 'templates/default_project'
    summary = 'EvasionWeb Project creation template.'
    vars = vars


class AppTemplate(Template):
    """Set up to create EvasionWeb App plugin.
    
    Once this is in the Python path, then the 
    app's package name can be included in the
    development.ini::
    
        :
        [app:main]
        web_modules = <package name>,
        :
    
    """
    _template_dir = 'templates/default_app'
    summary = 'EvasionWeb app plugin creation template.'
    vars = vars
    
    


class CreateAppCmd(Command):
    """
    Example command class. I'll do something useful with this 
    shortly.
    
    """
    # Parser configuration
    summary = "Create an Evasion Web app which can be used in an evasion project."
    usage = """ <new app name>

Create a new Evasion Web app called <new app name>.

This will create an initial python package you can then use.

"""
    group_name = "evasion"
    parser = Command.standard_parser(verbose=False)

    def command(self):
        import pprint
        print "Hello, CreateAppCmd script world!"
        print
        print "My options are:"
        print "    ", pprint.pformat(vars(self.options))
        print "My args are:"
        print "    ", pprint.pformat(self.args)
        print
        print "My parser help is:"
        print
        print self.parser.format_help()
