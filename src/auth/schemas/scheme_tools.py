from asgiref.sync import sync_to_async
from django.db.models import Model, QuerySet


@sync_to_async
def get_qset(qset:QuerySet, model:Model)->list[Model]:
    """get data from QuerySet"""
    resp = []
    for item in qset:
        if hasattr(model,'from_orm'):
            entity = model.from_orm(item)
        resp.append(entity)
    return resp

