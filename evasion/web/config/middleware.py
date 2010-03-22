"""Pylons middleware initialization
"""
import sys
import logging

from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from pylons.util import class_name_from_module_name

from evasion.web.config.environment import load_environment


def get_log():
    return logging.getLogger('evasion.web.config.middleware')


class WebAdminApp(PylonsApp):
    """
    This class overrides the controller resolution, so
    it will be looked for in multiple locations.
    
    """
    def find_controller(self, controller):
        """Locates a controller by attempting to import it then grab
        the SomeController instance from the imported module.
        
        Override this to change how the controller object is found once
        the URL has been resolved.
        
        """
        controller_paths = config['pylons.paths']['controllers']
        
        #get_log().debug("find_controller: looking for '%s' in paths '%s'." % (
        #    controller, 
        #    controller_paths
        #))
        
        # This is mostly a copy of the Pylons version we're overriding.
        # The only difference is that all controllers must be in the 
        # for <package> . <controllers dir> . <controller name>
        #
        full_module_name = controller
        
        # Check to see if we've cached the class instance for this name
        if controller in self.controller_classes:
            return self.controller_classes[controller]

        # Hide the traceback here if the import fails (bad syntax and such)
        __traceback_hide__ = 'before_and_this'
        
        importmod = full_module_name
        fromlist = full_module_name.split('.')
        # absolute imports only (level=0):
        get_log().debug("find_controller: import<%s> fromlist<%s>" % (importmod, fromlist))
        try:
            m = __import__(importmod, fromlist=fromlist, level=0)
            
        except:
            get_log().exception("find_controller: import<%s> fromlist<%s> Error - " % (importmod, fromlist))
            raise
            
        else:
            get_log().debug("find_controller: imported '%s' from '%s'." % (
                m, 
                full_module_name
            ))
        
        if hasattr(sys.modules[full_module_name], '__controller__'):
            mycontroller = getattr(
                sys.modules[full_module_name],
                sys.modules[full_module_name].__controller__
            )
                
        else:
            module_name = controller.split('.')[-1]
            class_name = module_name.title() + 'Controller'
            get_log().debug(
                "Found controller, module: '%s', class: '%s'",
                full_module_name, 
                class_name
            )
            mycontroller = getattr(sys.modules[full_module_name], class_name)
            
        self.controller_classes[controller] = mycontroller
            
        return mycontroller



def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    set_up = load_environment(global_conf, app_conf)
    middleware_list = set_up['middleware_list']

    # The Pylons WSGI app
    app = WebAdminApp()

    # Set up the middleware based on the list of provided middleware functions:
    #
    for middleware in middleware_list:
        try:
            get_log().debug("Calling middleware '%s' - " % middleware)
            app = middleware(app, global_conf, app_conf, middleware_list)
            
        except:
            get_log().exception("Error configuring middleware '%s' - " % middleware)

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_apps = [
            StaticURLParser(path) for path in config['pylons.paths']['static_files']
        ]
        app = Cascade(static_apps + [app,])


    return app



