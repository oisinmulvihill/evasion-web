"""
"""
import logging


class ModelManager(object):
    """
    """

    def __init__(self, global_conf, app_conf, dbsetup=False):
        """
        :param global_conf, app_conf: These are the configuration instances
        passed in from the environment. We store these for later use.
        """
        self.log = logging.getLogger('evasion.web.lib.modelmanager.ModelManager')
        self.modules = []
        self.global_conf = global_conf
        self.app_conf = app_conf
        self.dbsetup = dbsetup


    def isInSetup(self):
        """Called to check if 
        """
        return self.dbsetup


    def ready(self):
        """This is called once prior to init/create/destroy and could be 
        used to set up module wide connections or other such house keeping.
        """
        

    def connection(self):
        """Called to return a database connection.
        
        This connection can be used by each module when its
        init/create/destroy is called.
        
        """        

        
    def addModel(self, m):
        """Add a module which provides init, create, destroy.
        
        :param m: This is a tupple of two strings which are used 
        to import the module when the 'init' method is called. 
        The tupple has the form: ('from path', 'module') for 
        example: ('musing.post', 'postdb'). This is equivalent 
        to 'from musing.post import postdb'.            
        
        The imported module's init/create/destroy will be passed
        one argument which is the instance of the ModelManager.
        
        """
        self.log.debug("addModel: storing '%s' for later use." % str(m))
        self.modules.append(m)
        
        
    def init(self):
        """Iterate through all the stored modules and call their init.
        
        The self.connection will contain whatever dbconnection returned.
        
        """
        if self.isInSetup():
            self.log.warn("init: ignoring this step as the app is in db create/destroy mode (dbsetup=%s)." % self.dbsetup)
            return 

        self.ready()
            
        self.log.debug("init: calling init for each of the %d modules present." % len(self.modules))
        
        for mod, fromlist in self.modules:
            self.log.debug("init: calling %s.init(...)." % mod)
            m = __import__(mod, fromlist=fromlist)
            m.init(self)
        
        
    def create(self):
        """Iterate through all the stored modules and call their create.
        
        The self.connection will contain whatever dbconnection returned.
        
        """
        self.ready()

        self.log.debug("create: calling create for each of the %d modules present." % len(self.modules))
        
        for mod, fromlist in self.modules:
            self.log.debug("create: calling %s.create(...)." % mod)
            m = __import__(mod, fromlist=fromlist)
            m.create(self)
        
        
    def destroy(self):
        """Iterate through all the stored modules and call their destroy.
        
        The self.connection will contain whatever dbconnection returned.
        
        """
        self.ready()

        self.log.debug("destroy: calling destroy for each of the %d modules present." % len(self.modules))
        
        for mod, fromlist in self.modules:
            self.log.debug("destroy: calling %s.destroy(...)." % mod)
            m = __import__(mod, fromlist=fromlist)
            m.destroy(self)

