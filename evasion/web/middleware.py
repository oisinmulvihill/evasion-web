# -*- coding: utf-8 -*-
"""Pylons middleware initialization
"""
import sys
import logging
import traceback

import simplejson
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from pylons.util import class_name_from_module_name
from weberror.errormiddleware import Supplement
from weberror.errormiddleware import ErrorMiddleware
from weberror.errormiddleware import ResponseStartChecker


from evasion.web.environment import load_environment


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

    enable_default_errorhandling = app_conf.get('enable_default_errorhandling', 'true')
    if enable_default_errorhandling.lower() == 'true':
        get_log().info("load_environment: enabling default error handling middleware (enable_default_errorhandling = true).")
        if asbool(full_stack):
            # Handle Python exceptions
            app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

            # Display error documents for 401, 403, 404 status codes (and
            # 500 when debug is disabled)
            if asbool(config['debug']):
                app = StatusCodeRedirect(app)
            else:
                app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])
    else:
        get_log().warn("load_environment: default error handling middleware disabled (enable_default_errorhandling = false).")


    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_apps = []
        for p in  config['pylons.paths']['static_files']:
            # unwind the list of static paths:
            if type(p) in (type([]), type((0,))):
                for a in p:
                    static_apps.append(StaticURLParser(a))
            else:
                static_apps.append(StaticURLParser(p))

        app = Cascade(static_apps + [app,])


    return app


class ErrorHandler(ErrorMiddleware):
    """Based on weberror.errormiddleware:ErrorMiddleware

    Override the error handler and implement a different exception
    handler, to return a JSON encoded dict for newman-client to handle
    more easily.

    """
    def __init__(self, *args, **kwargs):
        ErrorMiddleware.__init__(self, *args, **kwargs)
        self.log = logging.getLogger('evasion.web.middleware.ErrorHandler')
        self._logTheTraceback = False


    def showTracebacks(self):
        """ Enable the logging of tracebacks to aid internal error debugging. """
        self._logTheTraceback = True


    def __call__(self, environ, start_response):
        """
        The WSGI application interface.
        """
        # We want to be careful about not sending headers twice,
        # and the content type that the app has committed to (if there
        # is an exception in the iterator body of the response)
        if environ.get('paste.throw_errors'):
            return self.application(environ, start_response)
        environ['paste.throw_errors'] = True

        try:
            __traceback_supplement__ = Supplement, self, environ
            sr_checker = ResponseStartChecker(start_response)
            app_iter = self.application(environ, sr_checker)
            return self.make_catching_iter(app_iter, environ, sr_checker)

        except:
            exc_info = sys.exc_info()
            try:
                response = self.exception_handler(start_response, exc_info, environ)
                if isinstance(response, unicode):
                    response = response.encode('utf8')
                return [response]

            finally:
                # clean up locals...
                exc_info = None


    def exception_handler(self, start_response, exc_info, environ):
        """Override base class version to return JSON instead.

        The HTTP status code will also be set

        :returns: JSON encoded dict(
                exception='a.b.c.Exception',
                value='exception message'
            )

        """
        returned_status = '500 Internal Server Error'
        self.log.error("""exception_handler exc_info:\n%s\n""" % str(exc_info))
        exc_type, exc_value, trace_back = exc_info

        if self._logTheTraceback:
            self.log.warn("** TRACEBACK DEBUG\n%s\n" % ("".join(traceback.format_tb(trace_back))))

        try:
            # Set up a 400 Bad Request message.
            #
            returned_status = "400 Bad Request"


            # Give the import path of exc_type. This will be used on the other
            # side to import and re-raise the same exception and error message.
            #
            exception_name = "%s.%s" % (exc_type.__module__, exc_type.__name__)

            returned = dict(
                exception=exception_name,
                value=str(exc_value)
            )

        except:
            self.log.exception("exception_handler failed to handle exception! ")

            returned = dict(
                exception='SystemError',
                value='Internal Server Exception :('
            )

        # Decide which response to return 4XX -> 5XX:
        #
        start_response(
            returned_status,
            [('content-type', 'text/html; charset=utf8')],
            exc_info
        )

        return simplejson.dumps(returned)


def rest_errorhandling_setup(app, global_conf, app_conf, middleware_list):
    """Configure the custom error handling.
    """
    get_log().info("rest_errorhandling_setup: setting up special REST error middleware.")

    app = ErrorHandler(app)

    # Aid debugging of internal errors rather then deliberately raised exceptions.
    debug = global_conf.get('debug', 'false')
    if debug == 'true':
        get_log().warn("global_conf: [DEFAULT] debug = true enabling traceback printing.")
        app.showTracebacks()

    return app
