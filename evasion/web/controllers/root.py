import logging

from routes import url_for
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from webadmin.lib.base import BaseController, render




class RootController(BaseController):

    def __init__(self, *args, **kw):
        BaseController.__init__(self, *args, **kw)
        self.log = logging.getLogger('webadmin.controllers.root.RootController')
        

    def index(self):
        return render('/root.mako')


