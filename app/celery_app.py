from celery import Celery
import os

def make_celery(app_name=__name__):
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    return Celery(app_name, backend=redis_url, broker=redis_url)

celery = make_celery()

def init_celery(app, celery_instance):
    """
    Updates Celery configuration with Flask app config.
    Binds tasks to Flask app context.
    """
    celery_config = {key: value for key, value in app.config.items() if key.startswith('CELERY_')}
    celery_instance.conf.update(celery_config)
    
    if 'broker_url' not in celery_instance.conf and 'CELERY_BROKER_URL' not in celery_config:
        celery_instance.conf.broker_url = app.config.get('REDIS_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    if 'result_backend' not in celery_instance.conf and 'CELERY_RESULT_BACKEND' not in celery_config:
        celery_instance.conf.result_backend = app.config.get('REDIS_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

    
    class ContextTask(celery_instance.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery_instance.Task = ContextTask