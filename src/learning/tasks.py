import json

import utils
from app import app
from learning.aggregator import Aggregator

# from learning.config import CONFIG
from learning.trainer import Trainer

# from celery.signals import celeryd_after_setup


# @celeryd_after_setup.connect
# def capture_worker_name(sender, headers=None, body=None, **kwargs):
#     sender_name = str(sender).split("@")[0]
#     print(f"sender: {sender}, sender_name: {sender_name}")
#     CONFIG["sender_name"] = sender_name


@app.task()
def celery_aggregate(list_local_models: dict, global_epoch: int) -> None:
    aggr = Aggregator()
    print(list_local_models.keys())
    aggregated_model = aggr.aggregate(list_local_models, global_epoch)
    return aggregated_model


@app.task()
def celery_train(global_model, global_epoch: int, queue_name: str) -> None:
    trainer = Trainer()
    trained_model = trainer.train(queue_name, global_model, global_epoch)
    model_weights = json.dumps(trained_model, cls=utils.NumpyArrayEncoder)
    return model_weights
