from celery import Celery
from celery.schedules import crontab
import os


def make_celery(app=None):
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    celery = Celery(
        'hms_tasks',
        broker=redis_url,
        backend=redis_url,
        include=['tasks.jobs']
    )

    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',
        enable_utc=True,

        # 🔥 SCHEDULER CONFIG
        beat_schedule={

            # 🟢 DAILY REMINDER (REAL)
            'daily-reminders': {
                'task': 'tasks.jobs.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),  # every day 8 AM
            },

            # 🟢 MONTHLY REPORT (REAL)
            'monthly-reports': {
                'task': 'tasks.jobs.send_monthly_reports',
                'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st day
            },

            # TEST MODE (UNCOMMENT FOR DEMO)
             #'test-reminder': {
                 #'task': 'tasks.jobs.send_daily_reminders',
                 #'schedule': 30.0,  # every 30 seconds
             #},
        }
    )

    # 🔥 Flask context support
    if app:
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Create celery instance
celery_app = make_celery()