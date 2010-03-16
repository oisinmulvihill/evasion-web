"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

siteversion = '1.0.0'

# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password
from routes import url_for


# Import the auth detail recovery
from authdetails import auth_details
from authdetails import is_authenticated

