from telegram.bot import Component as BotComponent
from telegram.banning_feature import Component as BanningFeatureComponent
from telegram.ping_feature import Component as PingFeatureComponent
from telegram.testing_feature import Component as TestingFeatureComponent
from telegram.voice_to_text_feature import Component as VoiceToTextFeatureComponent
from telegram import settings_feature
from telegram.limit_joining_feature import JoinLimiterComponent

__all__ = ['BotComponent',
           'BanningFeatureComponent',
           'PingFeatureComponent',
           'VoiceToTextFeatureComponent',
           'settings_feature',
           'JoinLimiterComponent',
           'TestingFeatureComponent']
