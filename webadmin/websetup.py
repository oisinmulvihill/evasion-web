"""Setup the webadmin application"""
import logging

from webadmin.config.environment import load_environment


def get_log():
    return logging.getLogger('evasion.web.websetup')
    

def setup_app(command, conf, vars):
    """Place any commands to setup webadmin here"""
    load_environment(conf.global_conf, conf.local_conf)
    
    get_log().info("Creating DB")
    from commoncouchdb import db
    db.create()
    
