"""Pylons environment configuration"""
import os
import pprint
import logging

from mako.lookup import TemplateLookup
from pylons import config
from pylons.error import handle_mako_error

import evasion.web.lib.app_globals as app_globals
import evasion.web.lib.helpers
from evasion.web.config.routing import make_map


def get_log():
    return logging.getLogger('evasion.web.config.environment')


def default_middleware(app, global_conf, app_conf, middleware_list):
    """
    Add the default pylons Routing/Session/Cache Middleware.
    """
    from routes.middleware import RoutesMiddleware
    from beaker.middleware import CacheMiddleware, SessionMiddleware
    
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)
    
    return app


def default_auth(app, global_conf, app_conf, middleware_list):
    """
    Add the default evasion file based authentification.
    """
    from evasion.web.config.repozewhomid import add_auth
    
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
    
    return app


def load_environment(global_conf, app_conf, websetup=False):
    """Configure the Pylons environment via the ``pylons.config``
    object

    :returns: return set up recovered which will be used
    used in websetup.py or middleware.py
    
        dict(
            loaded_modules = [ ... ],
            setup_app_list = [ ..setup_app function list..],
            middleware_list = [ ..functions like default_middleware or default_auth.. ],
        )

    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    controller_list = []
    template_list = []
    static_dir_list = []
    setup_app_list = []
    loaded_modules = []
    middleware_list = [
        default_middleware, 
        default_auth,
    ]
    
    # Create the base routing
    map = make_map()
    
    # Create globals loaded_modules can add sections to:
    g = app_globals.Globals()

    # Load the evasion.web modules we are using into the webapp.
    # Under the [app:main] section should be like
    # webadmin_modules = something, something else, etc
    # A safe default is:
    #
    # webadmin_modules = evasion.web 
    #
    # If nothing is found in the configuration then the default 
    # 'evasion.web' interface will be used.
    #
    loaded_modules = app_conf.get('web_modules', 'evasion.web')
    loaded_modules = [m for m in loaded_modules.split(',') if m]
    get_log().info("load_environment: director evasion.web modules '%s'." % loaded_modules)
    
    module_rdicts = []
    
    # Attempt to load and set up the evasion.web modules listed in 
    # the config file. These modules need to be in the path that 
    # the evasion-evasion.web looks in for python imports.
    #
    for module in loaded_modules:
        try:
            get_log().info("load_environment: loading module '%s'." % module)
            importmod = module
            fromlist = module.split('.')
            # absolute imports only (level=0):
            #get_log().debug("load_environment: import<%s> fromlist<%s>" % (importmod, fromlist))
            m = __import__(importmod, fromlist=fromlist, level=0)
            
        except ImportError, e:
            get_log().error("load_environment: unable to load module '%s'." % module)
            
        else:
            try:
                rdict = m.configure(map, global_conf, app_conf, websetup)
                controller_list.append(rdict['controllers'])
                static_dir_list.append(rdict['static'])
                template_list.append(rdict['templates'])
                map = rdict['map']
                if rdict['middleware']:
                    get_log().debug("load_environment: appending middleware to list: %s" % rdict['middleware'])
                    middleware_list.append(rdict['middleware'])
                if rdict['setup_app']:
                    get_log().debug("load_environment: appending to setup app list: %s" % rdict['setup_app'])
                    setup_app_list.append(rdict['setup_app'])
                g.__dict__[module] = rdict['g']
                module_rdicts.append((module, rdict))
                get_log().debug("load_environment: configure() returned:\n%s\n" % pprint.pformat(rdict))

            except SystemExit, e:
                raise

            except:
                get_log().exception("load_environment: module '%s' configuration error - " % module)
                
    # Save the routes mapping:
    config['routes.map'] = map
    
    paths = dict(
        root=root,
        controllers=controller_list, 
        static_files=static_dir_list,
        templates=template_list ,
    )

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='evasion.web', paths=paths)

    # Store the site wide routes map:
    config['routes.map'] = map
    
    # Store the modules for later use:
    g.modules = loaded_modules
    
    # Store the site wide globals:
    config['pylons.app_globals'] = g
    
    config['pylons.h'] = evasion.web.lib.helpers

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'])

    # Store the modules for later reference
    config['evasion.web.modules'] = {}
    for module, rdict in module_rdicts:
        kind = rdict['kind']
        m = config['evasion.web.modules'].get(kind, dict(kind=kind, modules=[]))
        m['modules'].append(dict(
            module=module, 
            name=rdict['name'],
            desc=rdict['desc'],
            setup=rdict,
        ))
        config['evasion.web.modules'][kind] = m

        
    # Used in middleware.py / websetup function:
    #
    return dict(
        loaded_modules = loaded_modules,
        setup_app_list = setup_app_list,
        middleware_list = middleware_list,
    )



