"""Pylons environment configuration"""
import os
import pprint
import logging

from mako.lookup import TemplateLookup
from pylons import config
from pylons.error import handle_mako_error

import webadmin.lib.app_globals as app_globals
import webadmin.lib.helpers
from webadmin.config.routing import make_map


def get_log():
    return logging.getLogger('webadmin.config.environment')


def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    controller_list = []
    template_list = []
    static_dir_list = []
    modules = []

    # Create the base routing
    map = make_map()

    # Check if the director is present then ask for webadmin modules:
    from director.signals import SignalsSender
    director = SignalsSender()
    director.ping()
    modules.extend(director.webadminModules())
    
    get_log().info("load_environment: director webadmin modules '%s'." % modules)
    
    # Attempt to load and set up the webadmin modules the director
    # has returned. These modules need to be in the path that the
    # evasion-webadmin looks in for python imports.
    #
    for module in modules:
        try:
            get_log().info("load_environment: loading module '%s'." % module['webadmin'])
            importmod = module['webadmin']
            fromlist = module['webadmin'].split('.')
            # absolute imports only (level=0):
            #get_log().debug("load_environment: import<%s> fromlist<%s>" % (importmod, fromlist))
            m = __import__(importmod, fromlist=fromlist, level=0)
            
        except ImportError, e:
            get_log().error("load_environment: unable to load module '%s'." % module['webadmin'])
            
        else:
            try:
                rdict = m.configure(map)
                controller_list.append(rdict['controllers'])
                static_dir_list.append(rdict['static'])
                template_list.append(rdict['templates'])
                map = rdict['map']
                get_log().debug("load_environment: configure() returned:\n%s\n" % pprint.pformat(rdict))

            except:
                get_log().exception("load_environment: module '%s' configuration error - " % module['webadmin'])

                
    # Save the routes mapping:
    config['routes.map'] = map
    
    paths = dict(
        root=root,
        controllers=controller_list, 
        static_files=static_dir_list,
        templates=template_list ,
    )

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='webadmin', paths=paths)

    config['routes.map'] = map
    # Store the modules for later use:
    g = app_globals.Globals()
    g.modules = modules
    config['pylons.app_globals'] = g
    config['pylons.h'] = webadmin.lib.helpers

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'])

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
