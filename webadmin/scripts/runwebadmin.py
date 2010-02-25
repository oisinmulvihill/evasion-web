"""
I took this from the pylons list:
   
   http://www.mail-archive.com/pylons-discuss@googlegroups.com/msg08951.html

This should allow me to bbfreeze the webadmin web server - Oisin 2009-12-03.


Run the standalone on the console similar to "paster serve".

This version imports the server and application rather than loading entry
points based on the ``use`` variables in the config file.  However, it does do
a string comparision on the ``use`` values and aborts if point to something
different than what it intends to load.

Make sure you've installed the application, Pylons, and any other dependencies
before running this.
"""
import os
import sys
import os.path
import logging
import threading
import logging.config
from optparse import OptionParser

from paste.deploy.loadwsgi import NicerConfigParser

# Server class and corresponding 'use=' value in config
SERVER_USE_VALUE = "egg:Paste#http"
from paste.httpserver import server_runner as server_factory


# Application factory and corresponding 'use=' value in config
APP_USE_VALUE = "egg:evasion-webadmin"
from webadmin.config.middleware import make_app as app_factory

def get_log():
    return logging.getLogger('webadmin')


class Run(object):    
    
    def __init__(self, ini_file):
        """
        Set up the configuration ready for main and appmain to use.
        
        :params ini_file: None or ini file used to configure the webapp 
        and logging. If this is None then the internal version will be 
        used in the webadmin.script directory
        
        """
        self.log = logging.getLogger('webadmin.scripts.runwebadmin.Run')

        # If nothing was given for the config file use our internal version.
        if not ini_file:
            self.iniFile = os.path.abspath(__file__)
        else:
            self.iniFile = os.path.abspath(ini_file)
            
        config_dir = os.path.dirname(__file__)
        self.iniFile = os.path.join(config_dir, 'development.ini')
        logging.config.fileConfig(self.iniFile)
        
        self.log.debug("init: config dir:'%s'" % config_dir)
        self.log.debug("init: self.iniFile:'%s'" % self.iniFile)
        
        self.cp = NicerConfigParser(self.iniFile)
        self.cp.read(self.iniFile)
        self.globalConf = self.cp.defaults()
        
        self.cp._defaults.setdefault("here", config_dir)
        self.cp._defaults.setdefault("__file__", self.iniFile)
        self.serverConf = self.getConfig(self.cp, "server:main", "egg:Paste#http")
        self.appConf = self.getConfig(self.cp, "app:main", "egg:evasion-webadmin")


    def getConfig(self, cp, section, expected_use_value):
        """Get a section from an INI-style config file as a dict.
        
        ``cp`` -- NicerConfigParser.
        ``section`` -- the section to read.
        ``expected_use_value`` -- expected value of ``use`` option in the section.
        
        Aborts if the value of ``use`` doesn't equal the expected value.  This
        indicates Paster would instantiate a different object than we're expecting.
        
        The ``use`` key is removed from the dict before returning.
        """
        defaults = self.cp.defaults()
        ret = {}
        for option in self.cp.options(section):
            if option.startswith("set "):  # Override a global option.
                option = option[4:]
            elif option in defaults:       # Don't carry over other global options.
                continue
            ret[option] = self.cp.get(section, option)
        use = ret.pop("use", "")
        if use != expected_use_value:
            msg = ("unexpected value for 'use=' in section '%s': "
                   "expected '%s', found '%s'")
            msg %= (section, expected_use_value, use)
            raise EnvironmentError(msg)
        return ret


    def appmain(self, isExit):    
        """
        Called to run inside its own thread once twisted has taken over 
        the main loop.
        
        """
        app = app_factory(self.globalConf, **self.appConf)
        serve = server_factory(app, self.globalConf, **self.serverConf)
        self.log.info("appmain: Serving webapp")
        serve(app)
    

    def main(self):
        """
        Called to run twisted in the mainloop so messaging will work correctly. 
        The webapp will be run via appmain.
        
        """
        import messenger        

        stomp_cfg = dict(
            host = self.cp.get("Messenger", "host"),
            port = int(self.cp.get("Messenger", "port")),
            username = self.cp.get("Messenger", "username"),
            password = self.cp.get("Messenger", "password"),
            channel = self.cp.get("Messenger", "channel"),
        )
        
        self.log.info("appmain: setting up stomp connection")
        messenger.stompprotocol.setup(stomp_cfg)
        
        self.log.info("appmain: running mainloop until done.")
        messenger.run(self.appmain)
        
        self.log.info("appmain: Exiting.")


def main():
    parser = OptionParser()
                      
    parser.add_option("--config", action="store", dest="config_filename", 
                    default=None,
                    help="This webadmin configuration file used at run time."
                    )
                      
    
    (options, args) = parser.parse_args()

    if options.config_filename and not os.path.isfile(options.config_filename):
        sys.stderr.write("The config file name '%s' wasn't found!\n" % options.config_filename)
        sys.exit(1)
        
    r = Run(options.config_filename)
    r.main()



