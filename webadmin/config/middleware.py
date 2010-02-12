"""Pylons middleware initialization
"""
import sys
import logging

from beaker.middleware import CacheMiddleware, SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
from pylons.util import class_name_from_module_name

from webadmin.config.repozewhomid import add_auth
from webadmin.config.environment import load_environment


def get_log():
    return logging.getLogger('webadmin.config.middleware')


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
        
        get_log().debug("find_controller: looking for '%s' in paths '%s'." % (
            controller, 
            controller_paths
        ))
        
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
        
        __import__(full_module_name)
        
        if hasattr(sys.modules[full_module_name], '__controller__'):
            mycontroller = getattr(sys.modules[full_module_name],
                sys.modules[full_module_name].__controller__)
                
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
    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = WebAdminApp()

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    # Set up the repoze.who auth:
    #
    sitename = app_conf.get('sitename','')
    sessionname = app_conf.get('beaker.session.key')
    sessionsecret = app_conf.get('beaker.session.secret')
    groupfile = app_conf.get('groupfile','')
    passwordfile = app_conf.get('passwordfile','')
    permissionfile = app_conf.get('permissionfile','')

    app = add_auth(
        app,
        sitename,
        sessionname,
        sessionsecret,
        passwordfile,
        groupfile,
        permissionfile
    )

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
