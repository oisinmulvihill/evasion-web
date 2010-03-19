
def configure(map, global_conf, app_conf, websetup):
    """
    Evasion Web default app. Used if no other is provided.
    
    :returns:
    
        dict(
            kind = 'web',
            name = 'Default',
            controllers = controllers_dir,
            static = static_dir,
            templates = templates_dir,
            map = map,
            g = g,
            setup_app = None,
            middleware = None,
        )
        
    The 'kind' is used to put modules into categories that can
    the be used to generate interface from. The two used most 
    are 'web' or 'admin'. The first is used for packages that 
    host content, where as the second is used for packages that 
    provide content editing or customisation and control of the 
    overall web app. The strings are arbitrary currently other
    could be used.
    
    The pylons configuration will be set up with a key called 
    'evasion.web.modules' after the environment has been loaded. 
    This will contain a dict of the loaded modules in the form:
    
        pylons.config['evasion.web.modules'] = dict(
            web = dict(
                kind='web',
                modules = [
                    # These are listed in the order read from
                    # the web_modules attribute.
                    dict(
                        # This is the same name as listed in the 
                        # web_modules attribute in the configuration.
                        module=<python module name>, 
                        name = '...Name as returnded by configure...',
                        desc = '...Description as returnded by configure...',
                        # The result as returned from configure(...)
                        # called at load environment time.
                        setup=dict(...),
                    ),
                    :
                    etc
                ]
            ),
            admin = dict(
                kind='admin',
                modules = [ ... ],
            )
            :
            etc
        )
        

    """
    import os
    import os.path
    
    import public as static
    import templates
    import controllers
    
    # Work out where the files are on disk:
    #
    controllers_dir = os.path.abspath(controllers.__path__[0])
    static_dir = os.path.abspath(static.__path__[0])
    templates_dir = os.path.abspath(templates.__path__[0])
    
    # Set up the routing for our URLs
    #
    base = 'evasion.web.controllers.%s'
    
    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller=base % 'error')
    map.connect('/error/{action}/{id}', controller=base % 'error')
    
    # Root site:
    map.connect('root', '/', controller=base % 'root', action='index')
    map.connect('login', '/login', controller=base % 'root', action='login')
    
    class EvasionWeb:
        def __init__(self):
            pass
            
    g = EvasionWeb()
    
    return dict(
        kind = 'web',
        name = 'default',
        desc = 'Default Web Package',
        controllers = controllers_dir,
        static = static_dir,
        templates = templates_dir,
        map = map,
        g = g,
        setup_app = None,
        middleware = None,
    )


