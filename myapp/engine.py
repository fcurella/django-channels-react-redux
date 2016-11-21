from django_react.engine import ActionEngine


class Engine(ActionEngine):

    def connect(self):
        super().connect()
        if self.message.user.is_authenticated():
            self.send({
                'type': 'SET_USER',
                'user': {
                    'username': self.message.user.username,
                }
            })

    def INCREMENT_COUNTER(self, message):
        self.send_to_group('broadcast', {'type': 'INCREMENTED_COUNTER', 'incrementBy': message['incrementBy']})
