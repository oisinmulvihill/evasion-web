# -*- coding: utf-8 -*-
"""
"""
import sys
import logging

import simplejson
from weberror.errormiddleware import Supplement
from weberror.errormiddleware import ErrorMiddleware
from weberror.errormiddleware import ResponseStartChecker


def get_log():
    return logging.getLogger('newman.accountservice.middleware')


class ErrorHandler(ErrorMiddleware):
    """Based on weberror.errormiddleware:ErrorMiddleware
    
    Override the error handler and implement a different exception
    handler, to return a JSON encoded dict for newman-client to handle
    more easily.
    
    """
    def __init__(self, *args, **kwargs):
        ErrorMiddleware.__init__(self, *args, **kwargs)
        self.log = logging.getLogger('newman.accountservice.middleware.ErrorHandler')

        
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
        
        try:
            # Set up a 400 Bad Request message.
            #
            returned_status = "400 Bad Request"
            
            exc_type, exc_value, traceback = exc_info
    
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
    
    return app