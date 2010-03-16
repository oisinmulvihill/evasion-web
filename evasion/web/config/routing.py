"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
import logging

from pylons import config
from routes import Mapper
from routes.util import controller_scan


def get_log():
    return logging.getLogger('webadmin.config.routing')
    

def directory_scanner():
    """
    Scan each of the controller paths and use the routes.util
    controller_scan() to recover from each path.
    
    This function uses the paths set up in config['pylons.paths']['controllers']
    by the load_environment step.
    
    """
    returned = []
    
    for directory in config['pylons.paths']['controllers']:
        get_log().debug("controller_scan: looking for controllers in '%s'." % directory)
        rc = controller_scan(directory)
        get_log().debug("controller_scan: found controllers '%s'." % str(rc))
        returned.extend(rc)
    
    return returned


def make_map():
    """Create the default mapper instance that the webadmin 
    modules will then add connections to.
    """
    map = Mapper(
        controller_scan=directory_scanner,
        directory = None,
        always_scan=config['debug']
    )
    map.minimization = False

    return map
