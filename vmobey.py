#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

'''vmobey - Execute actions in guest over VM channel (guest component)'''

DESCRIPTION =__doc__
VERSION = '0.1 / "Baba\'s Baklava"'
URL = 'https://github.com/doctor-love/vmobey'

import logging as _log
import subprocess
import argparse
import shlex
import glob
import time
import sys
import os


# -----------------------------------------------------------------------------
args = argparse.ArgumentParser(description=DESCRIPTION, epilog='URL: ' + URL)

args.add_argument(
    '-c', '--channel-dev', default='/dev/vport3p2', metavar='/path/to/vport',
    help='Channel vport device (default: "%(default)s")')

args.add_argument(
    '-a', '--actions-dir', default='/usr/lib/vmobey', metavar='/path/to/acts',
    help=(
        'Path to directory containing allowed '
        'action executables (default: "%(default)s")'))

args.add_argument(
    '-v', '--verbose', action='store_true', default=False,
    help='Enable verbose logging')

args.add_argument(
    '-V', '--version', action='version', version=VERSION,
    help='Show application version')

args = args.parse_args()

if args.verbose:
    log_level = _log.DEBUG

else:
    log_level = _log.INFO

_log.basicConfig(format='%(levelname)s: %(message)s', level=log_level)


# -----------------------------------------------------------------------------
def execute_action(timeout, action, params):
    _log.info(
        'Executing requested action "%s %s" with %i second(s) timeout'
        % (action, params, timeout))

    # In order to avoid shell breakout vulns, spawn process without shell
    action = [action]
    params = shlex.split(params)
    action.extend(params)

    try:
        cmd = subprocess.run(
            action, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=timeout)
 
        rc, output = cmd.returncode, cmd.stdout.decode('utf-8').strip()

    except subprocess.TimeoutExpired:
        error_msg = (
            'Action "%s" timed out after %i second(s)'
            % (' '.join(action), timeout))

        _log.error(error_msg)
        return 1, 'VMOBEY: ' + error_msg
            

    except Exception as error_msg:
        error_msg = (
            'Failed to execute action "%s": "%s"'
            % (' '.join(action), error_msg))

        _log.error(error_msg)
        return 1, 'VMOBEY: ' + error_msg

    _log.info('Result - RC: "%i", OUTPUT: "%s"' % (rc, output))
    return rc, output
 

# -----------------------------------------------------------------------------
if sys.version_info < (3, 5):
    _log.error('The script requires Python 3.5 or newer - sorry!')
    sys.exit(3)

acceptable_actions = glob.glob(args.actions_dir + '/*')
_log.debug('Allowed action executables: %s' % ', '.join(acceptable_actions))

try:
    _log.debug('Opening channel vport device "%s"' % args.channel_dev)
    channel = open(args.channel_dev, 'r+b', buffering=0)

except Exception as error_msg:
    _log.error('Failed to open channel vport: "%s"' % error_msg)
    sys.exit(1)

# -----------------------------------------------------------------------------
try:
    while True:
        recv = channel.readline()

        # TODO: Investigate why empty data is returned in read
        if not recv:
            time.sleep(1)
            continue 
        
        try:
            _log.debug('Recieved data over channel: "%s"' % str(recv))

            # Expected data format: "30 action_name arg-1 args-2 arg-3...\n"
            timeout, action, params = recv.decode('utf-8').split(' ', 2)
            timeout = int(timeout)
            params = params.strip()

        except Exception as error_msg:
            _log.error('Failed to decode recieved data: "%s"' % error_msg)
            continue
        
        # ---------------------------------------------------------------------
        action_path = os.path.join(args.actions_dir, os.path.basename(action))

        # Check if action executable is in "white list" directory
        if not action_path in acceptable_actions:
            _log.error('Requested action "%s" is not allowed' % action_path)

            status = '1 %s' % ('Action "%s" is not allowed' % action)
            channel.write(status.encode('utf-8'))
            continue
        
        rc, output = execute_action(timeout, action_path, params)
        status = '%i %s' % (rc, output)

        channel.write(status.encode('utf-8'))

except KeyboardInterrupt:
    _log.info('Interrupted by keyboard - exiting!\n')
    sys.exit(3)

except Exception as error_msg:
    _log.error('vmobey generated unhandled exception: "%s"' % error_msg)
    sys.exit(1)
