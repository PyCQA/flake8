import logging
import optparse
import os.path
import sys

if sys.version_info < (3, 0):
    import ConfigParser as configparser
else:
    import configparser

from . import utils

LOG = logging.getLogger(__name__)


class Option(object):
    def __init__(self, short_option_name=None, long_option_name=None,
                 # Options below here are taken from the optparse.Option class
                 action=None, default=None, type=None, dest=None,
                 nargs=None, const=None, choices=None, callback=None,
                 callback_args=None, callback_kwargs=None, help=None,
                 metavar=None,
                 # Options below here are specific to Flake8
                 parse_from_config=False
                 ):
        self.short_option_name = short_option_name
        self.long_option_name = long_option_name
        self.option_args = filter(None, (short_option_name, long_option_name))
        self.option_kwargs = {
            'action': action,
            'default': default,
            'type': type,
            'dest': dest,
            'callback': callback,
            'callback_args': callback_args,
            'callback_kwargs': callback_kwargs,
            'help': help,
            'metavar': metavar,
        }
        for key, value in self.option_kwargs.items():
            setattr(self, key, value)
        self.parse_from_config = parse_from_config
        self._option = optparse.Option(*self.option_args,
                                       **self.option_kwargs)
