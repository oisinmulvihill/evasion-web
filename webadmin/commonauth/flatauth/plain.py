"""
:mod:`plain` --- the plain modules
====================================

.. module:: plain
   :synopsis: provides handy functions...
   
.. moduleauthor:: Oisin Mulvihill<oisin@foldingsoftware.com>
.. sectionauthor:: Oisin Mulvihill<oisin@foldingsoftware.com>

.. versionadded:: 1.0

"""
import os
import csv
import pprint
import os.path
import logging
import StringIO

import fcrypt


def get_log():
    return logging.getLogger('commonauth.flatauth.plain')


# Windows/Linux compatible crypt function. The crypt_check in examples is unix only.
#
# from repoze.who.plugins.htpasswd import HTPasswdPlugin #, crypt_check
#
def password_check(password, hashed):
    """
    Used to check if the given password is equal to given encrypted password.

    :param password: This is the plain text password.
    :param arg2: This is the encrypted value, created from an 
       earlier call to encrypt().
       
    :returns: True | False to say whether the passwords
       match | don't match.
    
    """
    if not password:
        return False

    if not hashed:
        return False
    
    mhash = fcrypt.crypt(password, 'cE')
    get_log().debug("crypt_check: given hash<%s> generated hash <%s>" % (hashed, mhash))
    return hashed == mhash


def encrypt(password):
    """
    Used to create a password that can be stored safely somewhere.

    :param password: This is the plain text password.
       
    :returns: the result of an fcrypt.crypt(...) call.
    
    """
    if not password:
        return ValueError("The password is not a valid string!")

    return fcrypt.crypt(password, 'cE')
  

class PlainAuthenticatorMetadataProvider(object):
    """
    This implements a combination of the repose.who IAuthenticatorPlugin
    and IMetadataProvider.

    This class loads a CSV file which contains the following fields::

        username, password, firstname, lastname, email
        bob, password, Bob, Sproket, bob@example.com
        :
        etc

    The password is encrypted and generated by the `encrypt` function that
    is provided in the `plain` module.

    The given CSV is loaded at start up time. It is used for user
    authentication and to decorate the environment with the firstname
    and lastname fields for the matching username. The extra field
    name is created as a convience for '%s %s' % (firstname, lastname)
    
    """
    FIELDNAMES = ['username', 'password', 'firstname', 'lastname', 'email']
    
    def __init__(self, user_details):
        """Load the user details recovered from a file.

        :param user_details: This is a string of lines read from
            the user data CSV file.
            
        """
        self.userDetails = {}
        
        s = StringIO.StringIO(user_details)
        reader = csv.DictReader(s, fieldnames=self.FIELDNAMES)
        
        # Skip headers or it will get added as a user!!
        reader.next()
        
        try:
            for row in reader:
                # No check for duplicate usernames is done! The
                # last will over write any previous entry.
                username = row['username'].strip()
                password = row['password'].strip()
                firstname = row['firstname'].strip()
                lastname = row['lastname'].strip()
                email = row['email'].strip()
                name = "%s %s" % (firstname, lastname)
                
                self.userDetails[username] = dict(
                    username=username,
                    password=password,
                    firstname=firstname,
                    lastname=lastname,
                    email=email,
                    name=name,
                )

        except csv.Error, e:
            raise ValueError('Error on line %d: %s' % (filename, reader.line_num, e))


    def authenticate(self, environ, identity):
        """
        Check the given auth details and if its ok return the
        userid for the given details.

        See: (IAuthenticatorPlugin)
            http://docs.repoze.org/who/narr.html#writing-an-authenticator-plugin

        :returns: None indicated auth failure.
            
        """
        returned = None
        
        login = identity.get('login')
        password = identity.get('password')
    
        # Recover the password and check the given one against it:
        user = self.userDetails.get(login)

        get_log().warn("""authenticate
        
        identity:
        %s
        
        login:
        %s
        
        user:
        %s
        
        """ % (identity, login, user))
        
        if user:
            get_log().debug("user '%s' hpw '%s'" % (user,user['password']))
            if password_check(password, user['password']):
                returned = user['username']

        return returned
        

    def add_metadata(self, environ, identity):
        """
        Add the firstname, lastname, name to the identity from
        the user details we recovered from the CSV data.

        See: (IMetadataProvider)
            http://docs.repoze.org/who/narr.html#writing-a-metadata-provider-plugin
        
        """
        userid = identity.get('repoze.who.userid')
        
        info = self.userDetails.get(userid)

        get_log().warn("""add_metadata
        
        identity:
        %s
        
        userid:
        %s
        
        info
        %s
        
        """ % (identity, userid, info))
        
        if info is not None:
            identity.update(info)


