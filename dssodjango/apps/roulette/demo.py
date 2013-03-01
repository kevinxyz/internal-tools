#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import random
import re
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import uuid

from tornado.options import define, options

from dssodjango.common_utils import get_app_credentials_from_auth_value, SSO_URL, add_query_parameter
from dssodjango.models import LDAPUser


define("port", default=8888, help="run on the given port", type=int)

APP_NAME = 'roulette'
STATIC = 'HEHEHEH'


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            #(r"/auth/login", AuthLoginHandler),
            #(r"/auth/logout", AuthLogoutHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/message/updates", MessageUpdatesHandler),
            ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            autoescape="xhtml_escape",
            )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        #user_json = self.get_secure_cookie("user")
        #print "JSON:%s" % user_json
        #if not user_json: return None
        #return tornado.escape.json_decode(user_json)
        app_auth_key = self.get_cookie('app_auth_key') # TODO(kevinx): HACK!!!
        if not app_auth_key:
            return None

        _, _, mail, displayName, _ = get_app_credentials_from_auth_value(app_auth_key)

        print "KEY: %s %s" % (app_auth_key, displayName)
        return {
            "displayName": "%s %d" % (displayName, random.randint(0, 100)),
            "mail": mail,
            #"last_name": "Chang",
            #"first_name": "Kevin",
            #"claimed_id": "https://www.google.com/accounts/o8/id?id=AItOawkBZpCfcHAX831venamxSBCYL0XP-RuWYU",
            #"name": "Kevin Chang"
        }

    def __get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)


class MainHandler(BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        print "MAIN %s" % self.current_user
        if not self.current_user:
            self.redirect(add_query_parameter(SSO_URL, 'service', APP_NAME))
        else:
            self.render("index.html", messages=MessageMixin.cache)


class MessageMixin(object):
    waiters = set()
    cache = []
    cache_size = 200

    def wait_for_messages(self, callback, cursor=None):
        cls = MessageMixin
        if cursor:
            index = 0
            for i in xrange(len(cls.cache)):
                index = len(cls.cache) - i - 1
                if cls.cache[index]["id"] == cursor: break
            recent = cls.cache[index + 1:]
            if recent:
                callback(recent)
                return
        cls.waiters.add(callback)

    def cancel_wait(self, callback):
        cls = MessageMixin
        cls.waiters.remove(callback)

    def new_messages(self, messages):
        cls = MessageMixin
        logging.info("Sending new message to %r listeners", len(cls.waiters))
        for callback in cls.waiters:
            try:
                callback(messages)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        cls.waiters = set()
        cls.cache.extend(messages)
        if len(cls.cache) > self.cache_size:
            cls.cache = cls.cache[-self.cache_size:]


class MessageNewHandler(BaseHandler, MessageMixin):
    #@tornado.web.authenticated
    def post(self):
        message = {
            "id": str(uuid.uuid4()),
            "from": self.current_user["displayName"],
            "body": self.get_argument("body"),
            }

        join_match = re.search(r'EMAIL ([\w\@\-\.]+) ENTERS',
                               self.get_argument("body"))
        if join_match:
            mail = join_match.group(1)
            print "JOINED! %s" %mail
            ldap_obj = LDAPUser.objects.get(mail=mail)
            message['from_photo_url'] = ldap_obj.photo_url
            message["html"] = self.render_string("joined.html",
                                                 message=message)
        else:
            message["html"] = self.render_string("message.html",
                                                 message=message)

        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)
        self.new_messages([message])


class MessageUpdatesHandler(BaseHandler, MessageMixin):
    #@tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        cursor = self.get_argument("cursor", None)
        self.wait_for_messages(self.on_new_messages,
                               cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(dict(messages=messages))

    def on_connection_close(self):
        self.cancel_wait(self.on_new_messages)


class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect(ax_attrs=["name"])

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect("/")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.write("You are now logged out")


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
