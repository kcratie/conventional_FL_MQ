import configparser

from celery import Celery

from learning.aggregator import Aggregator
from learning.tasks import celery_aggregate, celery_train

config = configparser.ConfigParser()
config.read("./config.ini")

NUM_TRAINERS = int(config["DISTRIBUTION"]["NUM_TRAINERS"])
NUM_COMMUNICATION_ROUNDS = int(config["TRAINING"]["NUM_COMMUNICATION_ROUNDS"])


def main():
    list_local_models = {}
    for r in range(NUM_COMMUNICATION_ROUNDS):
        print("ROUND", r)
        agg = Aggregator()
        aggregated_model = agg.aggregate(
            list_local_models=list_local_models, global_epoch=r
        )
        result_list = []
        for idx in range(1, NUM_TRAINERS + 1):
            res = celery_train.apply_async(
                kwargs={
                    "global_model": aggregated_model,
                    "global_epoch": r,
                    "queue_name": f"trainer{idx}",
                },
                queue=f"trainer{idx}",
            )
            result_list.append(res)
        for idx in range(1, NUM_TRAINERS + 1):
            list_local_models[f"trainer{idx}"] = result_list[idx - 1].get(
                propagate=False
            )

        # res1 = celery_train.apply_async(kwargs={"global_model": aggregated_model, "global_epoch": r, "queue_name": 'trainer1'},queue='trainer1')
        # res2 = celery_train.apply_async(kwargs={"global_model": aggregated_model, "global_epoch": r, "queue_name": 'trainer2'},queue='trainer2')
        # list_local_models['trainer1'] = res1.get(propagate=False)
        # list_local_models['trainer2'] = res2.get(propagate=False)


if __name__ == "__main__":
    main()
