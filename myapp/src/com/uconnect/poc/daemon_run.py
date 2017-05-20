import time

from daemons import daemonizer

@daemonizer.run(pidfile="/tmp/sleepy.pid")
def sleepy(sleep_time):

    while True:

        time.sleep(sleep_time)

sleep(20)  # Daemon started with 20 second sleep time.