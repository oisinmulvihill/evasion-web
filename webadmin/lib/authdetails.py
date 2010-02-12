"""
"""
import logging

from pylons import request


def get_log():
    return logging.getLogger("wwwoisin.lib.authdetails")
    

AUTHMETHOD = 'repoze.what.credentials'


def is_authenticated(req=None):
    """Called to check quickly check if any user auth details 
    are present in the environment.
    
    returned: 
        True: Yes, someone is logged in.
        False: No one is logged in.
    
    """
    rc = AUTHMETHOD in request.environ
        
#    msg = 'No'
#    if rc:
#        msg = 'Yes'
#    get_log().debug("is_authenticated: Logged in? %s " % msg)
    
    return rc
    

def auth_details():
    """Called to recover who is currently logged into the site 
    based on what the 'repoze.what.credentials', assuming they
    are present in the environment.
    
    returned:
    
        An empty {} if no-one has logged in.
        
      Or
      
        {
            'user' : Person(
                username='',
                password='',
                firstname='',
                lastname='',
                email='',
                name='',
            ),
            'groups' : [...],
            'permissions' : [...]
        }
    
    """
    returned = {}
    
    class Person(object):
        def __init__(self, user_identity):
            self.username=user_identity.get('username','')
            self.password=user_identity.get('password','')
            self.firstname=user_identity.get('firstname','')
            self.lastname=user_identity.get('lastname','')
            self.email=user_identity.get('email','')
            self.name=user_identity.get('name','')

    
    if is_authenticated():
        user = request.environ[AUTHMETHOD]
        user_identity = request.environ.get('repoze.who.identity')
        returned = dict(
            user = Person(user_identity),
            groups = user.get('groups', {}),
            permissions = user.get('permissions', {}),
        )
        
    return returned
    
        
