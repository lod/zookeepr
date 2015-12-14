# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
# 
#   License
# 
#     A copyright notice accompanies this license document that identifies
#     the copyright holders.
# 
#     Redistribution and use in source and binary forms, with or without
#     modification, are permitted provided that the following conditions are
#     met:
# 
#     1.  Redistributions in source code must retain the accompanying
# 	copyright notice, this list of conditions, and the following
# 	disclaimer.
# 
#     2.  Redistributions in binary form must reproduce the accompanying
# 	copyright notice, this list of conditions, and the following
# 	disclaimer in the documentation and/or other materials provided
# 	with the distribution.
# 
#     3.  Names of the copyright holders must not be used to endorse or
# 	promote products derived from this software without prior
# 	written permission from the copyright holders.
# 
#     4.  If any files are modified, you must cause the modified files to
# 	carry prominent notices stating that you changed the files and
# 	the date of any change.
# 
#     Disclaimer
# 
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND
#       ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#       TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#       PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#       EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#       TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#       ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#       TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
#       THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#       SUCH DAMAGE.
# 
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
  
"""
Decorators to control access to controllers and controller actions in a
Pylons or TurboGears 2 application.
  
All these utilities are also available in the 
:mod:`repoze.what.plugins.pylonshq` namespace.
  
"""
  
import inspect
import new
from decorator import decorator
  
from pylons import request, response
from pylons.controllers.util import abort
from .predicates import NotAuthorizedError
  
__all__ = ['ActionProtector', 'ControllerProtector']
  
  
class _BaseProtectionDecorator(object):
  
    default_denial_handler = None
  
    def __init__(self, predicate, denial_handler=None):
        """
        Make :mod:`repoze.what` verify that the predicate is met.
  
        :param predicate: A :mod:`repoze.what` predicate.
        :param denial_handler: The callable to be run if authorization is
            denied (overrides :attr:`default_denial_handler` if defined).
  
        If called, ``denial_handler`` will be passed a positional argument 
        which represents a message on why authorization was denied.
  
        """
        self.predicate = predicate
        self.denial_handler = denial_handler or self.default_denial_handler
  
  
  
class ActionProtector(_BaseProtectionDecorator):
    """
    Function decorator to set predicate checkers in Pylons/TG2 controller
    actions.
  
    .. attribute:: default_denial_handler = None
  
        :type: callable
  
        The default denial handler.
  
    """
  
    def __call__(self, action_):
        """
        Return :meth:`wrap_action` as the decorator for ``action_``.
  
        """
        return decorator(self.wrap_action, action_)
  
    def wrap_action(self, action_, *args, **kwargs):
        """
        Wrap the controller action ``action_``.
  
        :param action_: The controller action to be wrapped.
  
        ``args`` and ``kwargs`` are the positional and named arguments which
        will be passed to ``action_`` when called.
  
        It will run ``action_`` if and only if authorization is granted (i.e.,
        the predicate is met). Otherwise, it will set the HTTP status code
        (to 401 if the user is anonymous or 403 if authenticated) then, if
        defined, it will run the denial handler (if not, it will abort with
        :func:`pylons.controllers.util.abort`).
  
        It's worth noting that when the status code for the response is 401,
        that will trigger a :mod:`repoze.who` challenger (e.g., a login form 
        will be displayed).
  
        .. note::
  
            If you want to override the default behavior when authorization is
            denied (most likely), you should define just a denial handler. If
            you want to override the whole wrapper (very unlikely), it's safe
            to extend this class and override this method.
  
        """
        try:
            self.predicate.check_authorization(request.environ)
        except NotAuthorizedError, e:
            reason = unicode(e)
            if request.environ.get('repoze.who.identity'):
                # The user is authenticated.
                code = 403
            else:
                # The user is not authenticated.
                code = 401
            if self.denial_handler:
                response.status = code
                return self.denial_handler(reason)
            abort(code, comment=reason)
        return action_(*args, **kwargs)
  
  
class ControllerProtector(_BaseProtectionDecorator):
    """
    Class decorator to set predicate checkers in Pylons/TG2 controllers.
  
    .. attribute:: default_denial_handler = None
  
        :type: callable or str
  
        The default denial handler to be passed to :attr:`protector`.
  
        When it's set as a string, the resulting handler will be the attribute
        of the controller class whose name is represented by
        ``default_denial_handler``. For example, if ``default_denial_handler``
        equals ``"process_errors"`` and the decorated controller is
        ``NiceController``, the resulting denial handler will be:
        ``NiceController.process_errors``.
  
    .. attribute:: protector = ActionProtector
  
        :type: Subclass of :class:`ActionProtector`
  
        The action protection decorator to be added to 
        ``Controller.__before__``.
  
  
    """
  
    protector = ActionProtector
  
    def __call__(self, cls):
        """
        Add the :attr:`protector` decorator to the ``__before__`` method of the
        ``cls`` controller.
  
        """
        if inspect.isclass(cls):
            return self.decorate_class(cls)
        else:
            return self.decorate_instance(cls)
  
  
    def decorate_instance(self, obj):
        """Decorate the ``__before__`` method of a class instance."""
        cls = obj.__class__
        new_before = self.make_wrapped_method(cls)
        obj.__before__ = new.instancemethod(new_before, obj, cls)
        return obj
  
    def decorate_class(self, cls):
        """Decorate the ``__before__`` method of a class."""
        cls.__before__ = self.make_wrapped_method(cls)
        return cls
  
    def make_wrapped_method(self, cls):
        """Decorate the ``__before__`` method with the defined protector"""
        if callable(self.denial_handler) or self.denial_handler is None:
            denial_handler = self.denial_handler
        else:
            denial_handler = getattr(cls, self.denial_handler)
  
        if hasattr(cls, '__before__'):
            old_before = cls.__before__.im_func
        else:
            def old_before(*args, **kwargs): pass
            old_before.__name__ = '__before__'
  
        protector = self.protector(self.predicate, denial_handler)
        return protector(old_before)
