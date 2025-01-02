from celery import Celery
from configs import celery_conf as cfg


app = Celery(main='tasks',
             broker=cfg.broker_url,
             backend=cfg.result_backend,
             include=[
                 'works.add.tasks',
                 'works.run_tasks.tasks',
             ])

app.config_from_object('configs.celery_conf')
