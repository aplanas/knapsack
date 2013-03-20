import argparse
import datetime
import os
import subprocess
import time


def run_when(_args):
    print '{0} Running ... {1}'.format(datetime.datetime.now().isoformat(), _args)
    r = subprocess.call(_args, shell=True)
    print '{0} Result ... {1}'.format(datetime.datetime.now().isoformat(), r)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Use a file as a signal between machine.')
    parser.add_argument('--lock', help='Filename for the lock file')
    parser.add_argument('--run', help='Script to run when the lock is open')

    args = parser.parse_args()

    if not all((args.lock, args.run)):
        parser.print_help()
        exit(0)

    while True:
        if os.path.exists(args.lock):
            run_when(args.run.split())
            os.unlink(args.lock)
        time.sleep(2)
