import datetime

import telegram
import utils

class JoinLimiterComponent:
    name = 'join-limiter-feature'

    limiters: dict()

    @staticmethod
    def create(components, settings):
        self = JoinLimiterComponent()

        self.rate = settings['default-rate']
        time_obj = datetime.datetime.strptime(settings['default-sliding-window'], '%S.%f')
        self.window = datetime.timedelta(
            hours=time_obj.hour,
            minutes=time_obj.minute,
            seconds=time_obj.second,
            microseconds=time_obj.microsecond
        )
        self.bot = components.find(telegram.BotComponent).get()

        return self
