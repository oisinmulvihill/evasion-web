"""
I took this from the pylons list:
   
   http://www.mail-archive.com/pylons-discuss@googlegroups.com/msg08951.html

This should allow me to bbfreeze the evasion.web web server - Oisin 2009-12-03.


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

from paste.httpserver import serve
from paste.httpserver import server_runner
from paste.deploy.loadwsgi import NicerConfigParser

from evasion.web.config.middleware import make_app as app_factory


def get_log():
    return logging.getLogger('evasion.web.scripts.runweb')


class Run(object):    
    
    def __init__(self, ini_file=None, nologsetup=False):
        """
        Set up the configuration ready for main and appmain to use.
        
        :params ini_file: None or ini file used to configure the webapp 
        and logging. If this is None then the internal version will be 
        used in the evasion.web.script directory
        
        """
        self.log = logging.getLogger('evasion.web.scripts.runwebadmin.Run')
        config_dir = os.path.dirname(__file__)

        if not ini_file:
            # If nothing was given for the config file use our internal version.
            self.iniFile = os.path.join(config_dir, 'development.ini')
            self.log = logging.getLogger("init: using internal ini file '%s'." % self.iniFile)
            
        else:
            self.iniFile = os.path.abspath(ini_file)
            
        if not nologsetup:
            logging.config.fileConfig(self.iniFile)
        
        self.log.debug("init: config dir:'%s'" % config_dir)
        self.log.debug("init: self.iniFile:'%s'" % self.iniFile)
        
        self.cp = NicerConfigParser(self.iniFile)
        self.cp.read(self.iniFile)
        self.globalConf = self.cp.defaults()
        
        self.cp._defaults.setdefault("here", os.path.abspath(os.curdir))
        self.cp._defaults.setdefault("__file__", self.iniFile)
        self.serverConf = self.getConfig(self.cp, "server:main", "egg:Paste#http")
        self.appConf = self.getConfig(self.cp, "app:main", "egg:evasion-web")
        m = dict(
            state= self.cp.get('Messenger', 'state', 'off'),
            host = self.cp.get('Messenger', 'host', '127.0.0.1'),
            port = self.cp.get('Messenger', 'port', 61613),
            username = self.cp.get('Messenger', 'username', ''),
            password = self.cp.get('Messenger', 'password', ''),
            channel = self.cp.get('Messenger', 'channel', 'evasion'),
        )
        self.messengerConf = m
        
        # Only set up if running as part of the director under the webadminctrl 
        # controller. This runs the evasion.web as a thread instead of a separate
        # process.
        #
        self.directorIntegrationServer = None
        self.directorIntegrationIsRunning = False


    def setupapp(self):
        """
        Run the equivalent paster setup-app
        
        """
        from evasion.web import websetup
        
        class O:
            global_conf = self.globalConf
            local_conf = self.appConf
        
        command='?' # not sure what to do here
        conf = O()
        
        websetup.setup_app(command, conf, vars)
        

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


    def appmainSetup(self):
        """
        Called to create the wsgi app ready for appmain or 
        directorIntegration to use.
        
        """
        app = app_factory(self.globalConf, **self.appConf)
        return app
        

    def appmain(self, isExit):    
        """
        Called to run inside its own thread once twisted has taken over 
        the main loop.
        
        """
        app = self.appmainSetup()
        self.log.info("appmain: Serving webapp")
        server_runner(app, self.globalConf, **self.serverConf)


    def directorIntegrationStart(self):
        """
        Create a server which the director webadminctrl controller
        will use to run the webapp, when start is called. The 
        controller will also be able to stop the webapp via shutdown.
        
        """
        # You don't need this in integration mode as it is part
        # of the director's messaging system. If this is kept in
        # it will cause messages to be resent onto the message
        # bus in error.
        #
        #self.setUpStomp()
        
        self.log.info("directorIntegrationStart: creating wsgi_app")
        wsgi_app = self.appmainSetup()
        
        # Use threadpool to also get access to server_close()
        self.serverConf['use_threadpool'] = True
        
        # Don't start serving straigh away, return so I can
        # store the server handle to close it later.
        self.serverConf['start_loop'] = False
        
        self.log.info("directorIntegrationStart: creating server.")
        self.directorIntegrationServer = serve(wsgi_app, **self.serverConf)
        
        try:
            self.directorIntegrationIsRunning = True
            self.log.info("directorIntegrationStart: serving until stopped.")
            self.directorIntegrationServer.serve_forever()
            
        except KeyboardInterrupt:
            # allow CTRL+C to shutdown
            self.log.warn("directorIntegrationStart: KeyboardInterrupt! Stopping... ")
            
        except:
            self.log.exception("directorIntegrationStart Error - ")
            
        self.directorIntegrationIsRunning = False
        self.log.info("directorIntegrationStart: server stopped.")


    def directorIntegrationIsStarted(self):
        return self.directorIntegrationIsRunning
 

    def directorIntegrationStop(self):
        """Stop the server handling any more requests."""
        if not self.directorIntegrationServer:
            self.log.error("directorIntegrationStop: directorIntegrationStart not called to set up server!")
        else:
            self.log.info("directorIntegrationStop: telling server to close.")
            self.directorIntegrationServer.server_close()
            self.log.info("directorIntegrationStop: server close called ok.")


    def setUpStomp(self):
        """Connect to the broker so we can send/receive messages."""
        # Only import if we use it:
        from evasion import messenger        

        stomp_cfg = dict(
            host = self.cp.get("Messenger", "host"),
            port = int(self.cp.get("Messenger", "port")),
            username = self.cp.get("Messenger", "username"),
            password = self.cp.get("Messenger", "password"),
            channel = self.cp.get("Messenger", "channel"),
        )
        
        self.log.info("appmain: setting up stomp connection")
        messenger.stompprotocol.setup(stomp_cfg)


    def main(self):
        """
        Called to run twisted in the mainloop so messaging will work correctly. 
        The webapp will be run via appmain.
        
        """
        if self.messengerConf['state'] == 'on':
            # Only import if we use it:
            from evasion import messenger        
            self.setUpStomp()
        
            self.log.info("main: running mainloop until done.")
            messenger.run(self.appmain)
            self.log.info("main: Exiting.")
        
        else:
            self.log.info("main: running mainloop (no messenger).")
            self.appmain(None)
            self.log.info("main: Exiting.")


def main():
    parser = OptionParser()
                      
    parser.add_option("--config", action="store", dest="config_filename", 
                    default=None,
                    help="This evasion.web configuration file used at run time."
                    )
                      
    parser.add_option("--setup-app", action="store_true", dest="setupapp", 
                    default=False,
                    help="This does a paster setup-app with the --config option."
                    )
                      
    
    (options, args) = parser.parse_args()

    if options.config_filename and not os.path.isfile(options.config_filename):
        sys.stderr.write("The config file name '%s' wasn't found!\n" % options.config_filename)
        sys.exit(1)
        
    else:
        print "options.config_filename: ", options.config_filename

    r = Run(ini_file=options.config_filename)
    
    if options.setupapp:
        print("Running setup-app.")
        r.setupapp()
        
    else:
        print("Running webapp.")
        r.main()



