
def configure(map, global_conf, app_conf, websetup):
    """
    Evasion Web default app. Used if no other is provided.
    
    :returns:
    
        dict(
            controllers = controllers_dir,
            static = static_dir,
            templates = templates_dir,
            map = map,
            g = g,
            setup_app = None,
            middleware = None,
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
        controllers = controllers_dir,
        static = static_dir,
        templates = templates_dir,
        map = map,
        g = g,
        setup_app = None,
        middleware = None,
    )


