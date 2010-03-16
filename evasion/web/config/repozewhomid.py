import os
import os.path
import logging

from pylons import config
from routes import url_for
from repoze.what.middleware import setup_auth
# We need to set up the repoze.who components used by repoze.what for
# authentication
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.htpasswd import HTPasswdPlugin, crypt_check
# We'll use group and permission based exclusively on INI files
from repoze.what.plugins.ini import INIGroupAdapter
from repoze.what.plugins.ini import INIPermissionsAdapter
from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

from webadmin.commonauth.flatauth import plain


def get_log():
    return logging.getLogger('webadmin.config.repozewhomid')


def add_auth(app, sitename, sessionname, sessionsecret, password_file, groups_file, permissions_file):
    """
    Add authentication and authorization middleware to the ``app``.

    :param app: The WSGI application.
    :param sitename: the site name used in basic auth box.
    :param sessionname: basic auth name and cookie name.
    :param sessionsecret: unique secret string used to protect sessions.
    :param groups_file: the ini file source for the groups information.
    :param passwd_file: the ini file source for the permission information.
    :return: The same WSGI application, with authentication and
        authorization middleware.
        
    """
    site = sitename
    cookie_secret = sessionsecret 
    cookie_name = 'authtkt'

    login_url = url_for('/login')
    login_handler = url_for('/login_handler')
    post_login_url = None
    logout_handler = url_for('/logout_handler')
    post_logout_url = None
    login_counter_name = None

    get_log().info("add_auth: adding user/group/permission file based setup.")

    if not os.path.isfile(password_file):
        raise ValueError("Unable to find password file '%s'!" % password_file)
    else:
        user_data_file = os.path.abspath(password_file)

    if not os.path.isfile(groups_file):
        raise ValueError("Unable to find groups file '%s'!" % groups_file)
    else:
        groups = os.path.abspath(groups_file)
        
    if not os.path.isfile(permissions_file):
        raise ValueError("Unable to find password file '%s'!" % permissions_file)
    else:
        permissions = os.path.abspath(permissions_file)
    
    basicauth = BasicAuthPlugin(site)

    # Recover the User details and load it for the CSV repoze plugin to handle:
    fd = open(user_data_file, 'r')
    user_data = fd.read()
    fd.close()
    passauth_and_metadata = plain.PlainAuthenticatorMetadataProvider(user_data)
                   
    form = FriendlyFormPlugin(
        login_url,
        login_handler,
        post_login_url,
        logout_handler,
        post_logout_url,
        login_counter_name=login_counter_name,
        rememberer_name='cookie'
    )

    cookie = AuthTktCookiePlugin(cookie_secret, cookie_name)

    identifiers = [('main_identifier', form), ('basicauth', basicauth), ('cookie', cookie)]

    challengers = [('form', form), ('basicauth', basicauth)]

    authenticators = [('htpasswd', passauth_and_metadata)]

    mdproviders = [('simplemeta', passauth_and_metadata)]

    groups = {'all_groups': INIGroupAdapter(groups)}
    permissions = {'all_perms': INIPermissionsAdapter(permissions)}

    app_with_auth = setup_auth(
        app = app,
        group_adapters = groups,
        permission_adapters = permissions, 
        identifiers = identifiers, 
        authenticators = authenticators,
        challengers = challengers, 
        mdproviders = mdproviders, 
        log_level = logging.DEBUG
    )

    get_log().info("add_auth: user/group/permission setup OK.")
        
    return app_with_auth
    
