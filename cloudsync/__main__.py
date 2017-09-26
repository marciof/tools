#!/usr/bin/env python3

# standard
from argparse import ArgumentParser
import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
import sys

# internal
from cloudsync.clients import box, onedrive
from cloudsync.error import Error
from cloudsync.state import FileState, PrefixedState

# FIXME: initial download vs change list
# FIXME: receive where to download to via command line
# FIXME: prevent overwriting existing files?
# FIXME: sandbox download folder (never modify anything outside of it)
# FIXME: rename start command to "download"?
# FIXME: state lock-file?

# FIXME: chmod -x __main__
# FIXME: error msg when no args
# FIXME: executable name when usage info

# https://github.com/OneDrive/onedrive-sdk-python
# https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/driveitem_delta

# https://ianhowson.com/blog/file-synchronisation-algorithms/

# https://github.com/box/box-python-sdk
# https://developer.box.com/v2.0/reference

app_name = 'cloud-sync'

syslog_handler = SysLogHandler(address = '/dev/log')
syslog_handler.ident = app_name + ': '

logger = logging.getLogger(app_name)
logger.setLevel(logging.DEBUG)
logger.addHandler(syslog_handler)

clients = {
    'box': box.BoxClient,
    'onedrive': onedrive.OneDriveClient,
}

def make_client(name):
    state = PrefixedState([name], FileState(app_name, logger))
    return clients[name](state, logger)

def do_login_command(args):
    client = make_client(args.service)

    if args.auth_url is None:
        client.login()
    else:
        client.authenticate_url(args.auth_url)

def do_start_command(args):
    client = make_client(args.service)
    client.authenticate_session()

    for change in client.list_changes():
        change.apply('foobar')

parser = ArgumentParser()
parser.add_argument('-v', help = 'verbose output', action = 'store_true',
    dest = 'is_verbose')

command_parser = parser.add_subparsers(dest = 'command')
command_parser.required = True

login_parser = command_parser.add_parser('login', help = 'login to service')
login_parser.add_argument('service', help = 'service', choices = clients)
login_parser.add_argument('auth_url', help = 'authentication URL', nargs = '?')
login_parser.set_defaults(func = do_login_command)

start_parser = command_parser.add_parser('start', help = 'start sync')
start_parser.add_argument('service', help = 'service', choices = clients)
start_parser.set_defaults(func = do_start_command)

def main(args = None):
    parsed_args = parser.parse_args(args)

    if parsed_args.is_verbose:
        logger.addHandler(StreamHandler())

    try:
        parsed_args.func(parsed_args)
    except KeyboardInterrupt as error:
        logger.exception(error)
    except Error as error:
        logger.exception(error)
        sys.exit(str(error))

if __name__ == '__main__':
    main()
