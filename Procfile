web: gunicorn apollo.wsgi --log-file -
worker: celery worker --app=apollo.tasks -B --loglevel=info