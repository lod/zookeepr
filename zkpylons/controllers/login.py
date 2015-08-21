from pylons import request, response, session, tmpl_context, config, url
from pylons.controllers.util import redirect

from zkpylons.lib.base import BaseController, render
from zkpylons.lib.helpers import flash

import logging
log = logging.getLogger(__name__)


class LoginController(BaseController):
    def login(self):
        log.warning("LOGIN 1")
        log.debug(request.environ)

        login_counter = request.environ.get('repoze.who.logins')
        if login_counter > 0:
            flash('Wrong credentials')
        tmpl_context.login_counter = login_counter
        tmpl_context.came_from = request.params.get('came_from') or url('/')
        return render('login.mako')

    def login_handler(self):
        pass

    def post_login(self):
        log.warning("LOGIN 2")
        identity = request.environ.get('repoze.who.identity')
        came_from = str(request.params.get('came_from', '')) or url('/')
        if not identity:
            login_counter = request.environ.get('repoze.who.logins') + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        redirect(came_from)

    def logout_handler(self):
        log.warning("LOGOUT 1")
     
    def post_logout(self):
        log.warning("LOGOUT 2")
        redirect('/')
