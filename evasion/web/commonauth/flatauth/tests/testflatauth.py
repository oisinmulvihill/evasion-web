"""
Exercise the flatauth module as much as I can.

Oisin Mulvihill
2009-05-20

"""
import unittest

import commonauth
from commonauth.flatauth import plain


class FlatAuthTC(unittest.TestCase):
    """
    """

    def testPlainAuthenticatorMetadataProvider(self):
        """Test the CSV based authenticator/metadata provider.
        """
        user_data = """username, password, firstname, lastname, email
admin1, cEs0yeD9TWFzo, Admin, Istrator, admin@example.com
manager1, cEeBhGIVbBgvc, Bob, Wellington, bob@example.com
user1, cE49Oeqv/SEv2, Janet, Ganet, janet@example.com
"""
        # Test empty data doesn't cause any problems.
        p = plain.PlainAuthenticatorMetadataProvider("")

        env = {}
        identity = dict(login='admin1', password='admin1')
        self.assertEquals(p.authenticate(env, identity), None)

        env = {}
        identity = dict(userid='admin1')
        self.assertEquals(p.add_metadata(env, identity), None)

        # Ok, now test with valid data:
        p = plain.PlainAuthenticatorMetadataProvider(user_data)

        env = {}
        identity = dict(login='user1', password='user1')
        self.assertEquals(p.authenticate(env, identity), 'user1')

        env = {}
        identity = dict(login='admin1', password='admin1')
        self.assertEquals(p.authenticate(env, identity), 'admin1')

        env = {}
        identity = {'repoze.who.userid':'admin1'}
        p.add_metadata(env, identity)    
        self.assertEquals(identity['firstname'], 'Admin')
        self.assertEquals(identity['lastname'], 'Istrator')
        self.assertEquals(identity['name'], 'Admin Istrator')
        self.assertEquals(identity['email'], 'admin@example.com')

        env = {}
        identity = {'repoze.who.userid':'manager1'}
        p.add_metadata(env, identity)
        p.add_metadata(env, identity)
        self.assertEquals(identity['firstname'], 'Bob')
        self.assertEquals(identity['lastname'], 'Wellington')
        self.assertEquals(identity['name'], 'Bob Wellington')
        self.assertEquals(identity['email'], 'bob@example.com')
        


    def testplain(self):
        """Test the functions provided in the plain module.
        """
        # Check the password checking function:
        #
        data_tests = [
            # format:
            #    (plain, cipher, crypt check result)
            #
            # OK data:
            ('admin1','cEs0yeD9TWFzo', True),
            ('manager1','cEeBhGIVbBgvc', True),
            ('user1','cE49Oeqv/SEv2', True),
            
            # Bad data:
            ('me','12345', False),
            ('','', False),
            ('',None, False),
            (None,None, False),            
        ]

        for plainpw, cipher, result in data_tests:
            self.assertEquals(
                plain.password_check(plainpw, cipher),
                result,
                "Failed test plainpw<%s>, cipher<%s>, expected result<%s>" % (plainpw, cipher, result)
            )

        # Now check the encrypt function used to generate cipher text:
        #
        plain.password_check(plain.encrypt('admin1'), 'cEs0yeD9TWFzo')
        plain.password_check(plain.encrypt('manager1'), 'cEeBhGIVbBgvc')
        plain.password_check(plain.encrypt('user1'), 'cE49Oeqv/SEv2')



