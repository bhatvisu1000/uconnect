# daemon.py
#https://www.python.org/dev/peps/pep-3143/

import time

from daemons.prefab import run

class SleepyDaemon(run.RunDaemon):

    def run(self):

        while True:

            time.sleep(1)
