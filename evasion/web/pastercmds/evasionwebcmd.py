"""
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
    var('license_name', 'License name'),
    var('zip_safe', 'True/False: if the package can be distributed as a .zip file',
        default=False),
]

class ProjectTemplate(Template):
    _template_dir = 'templates/default_project'
    summary = 'EvasionWeb Project creation template.'
    vars = vars

class AppTemplate(Template):
    _template_dir = 'templates/default_app'
    summary = 'EvasionWeb app plugin creation template.'
    vars = vars
    
    


class CreateAppCmd(Command):
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
