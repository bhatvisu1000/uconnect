from apscheduler.schedulers.background import BackgroundScheduler
#https://apscheduler.readthedocs.io/en/latest/userguide.html

# The "apscheduler." prefix is hard coded
scheduler = BackgroundScheduler({
    'apscheduler.jobstores.mongo': {
         'type': 'mongodb'
    },
    'apscheduler.jobstores.default': {
        'type': 'sqlalchemy',
        'url': 'sqlite:///jobs.sqlite'
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '20'
    },
    'apscheduler.executors.processpool': {
        'type': 'processpool',
        'max_workers': '5'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '3',
    'apscheduler.timezone': 'UTC',
})

scheduler.add_job(myTime,'interval',minutes=.10, id='myTime')
scheduler.print_jobs()
scheduler.start()
scheduler.remove_job('myTime')

'''
Scheduler events
It is possible to attach event listeners to the scheduler. Scheduler events are fired on certain occasions, and may carry additional information in them concerning the details of that particular event. It is possible to listen to only particular types of events by giving the appropriate mask argument to add_listener(), OR’ing the different constants together. The listener callable is called with one argument, the event object.

See the documentation for the events module for specifics on the available events and their attributes.
'''
# Example:
# Add listener to scheduler
def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')

scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)