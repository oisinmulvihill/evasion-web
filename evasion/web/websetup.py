"""Setup the webadmin application"""
import logging

from webadmin.config.environment import load_environment


def get_log():
    return logging.getLogger('evasion.web.websetup')
    

def setup_app(command, conf, vars):
    """
    Load the environment then run each modules setup_app 
    if one was recovered.
    
    """
    set_up = load_environment(conf.global_conf, conf.local_conf, websetup=True)
    
    setup_app_list = set_up['setup_app_list']
    
    # Call each modules setup app:
    #
    for setupapp in setup_app_list:
        try:
            get_log().debug("setup_app: calling for '%s'." % setupapp)
            setupapp(command, conf, vars)

        except SystemExit, e:
            raise            

        except:
            get_log().exception("Error when calling '%s' - " % setupapp)
            
    
