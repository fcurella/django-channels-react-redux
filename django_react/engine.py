from channels import Group
from django.contrib.auth import authenticate, login, get_user_model

import json

User = get_user_model()


def send_action(group_name, action):
    """
    Convenience method to dispatch redux actions from channels.

    Usage::

        send_action("group_name", {
            "type": "MY_ACTION",
            "payload": {
                "id": 1,
                "name": "Lorem",
            }
        })
    """
    data = {
        'text': json.dumps(action),
    }
    Group(group_name).send(data)

    
class ActionEngine(object):
    """A simple dispatcher that consumes a Redux-style action and routes
    it to a method on the subclass, using the `action.type`.
    E.g. If an action comes in {type: 'login', user: 'bob'}, it will
    call the `LOGIN` method, passing in the the asgi message and parsed
    action.
    This is a very simplistic router and likely not ideal for longer-term
    since it ties the React client-side actions, to the network procedure
    calling protocol, to the server-side method definition. It also
    effectively exposes the Python methods to the client which could
    be a security risk, though we do mitigate by uppercasing the requested
    method which so not expose protected methods.
    Callers should use the `ActionEngine.dispath(message)`. Subclasses
    can use the `add` and `send` methods.
    """
    @classmethod
    def dispatch(cls, message):
        engine = cls(message)

        # Parse the websocket message into a JSON action
        action = json.loads(message.content['text'])

        # Simple protection to only expose upper case methods
        # to client-side directives
        action_type = action['type'].upper()
        if hasattr(engine, action_type):
            method = getattr(engine, action_type)
            return method(action)
        else:
            raise NotImplementedError('{} not implemented'.format(action_type))

    def __init__(self, message):
        self.message = message

    def get_control_channel(self, user=None):
        # Current control channel name, unless told to return `user`'s
        # control channel
        if 'user' not in self.message.channel_session:
            return None
        if user is None:
            user = self.message.channel_session['user']
        return 'user.{0}'.format(user)

    def add(self, group):
        Group(group).add(self.message.reply_channel)

    def send(self, action, to=None):
        if to is None:
            to = self.message.reply_channel
        to.send({
            'text': json.dumps(action),
        })

    def send_to_group(self, group, action):
        self.send(action, to=Group(group))

    def connect(self):
        control = self.get_control_channel()
        if control is not None:
            self.add(control)
        self.add('broadcast')

    def disconnect(self):
        # Discard the channel from the control group
        control = self.get_control_channel()
        if control is not None:
            Group(control).discard(
                self.message.reply_channel
            )
