from typing import Type

from asgiref.sync import sync_to_async, async_to_sync
from django.db.models import Model, QuerySet
from logrich.logger_ import log # noqa
from pydantic import BaseModel


# @sync_to_async
# @async_to_sync
async def get_qset(qset:QuerySet, model:Type[BaseModel])->list[BaseModel]:
    """get data from QuerySet"""
    # https://blog.etianen.com/blog/2013/06/08/django-querysets/
    resp = []
    if qset.aexists():
        # for item in qset.iterator():
        async for item in qset.aiterator():
            # log.debug(item)
            if hasattr(model,'from_orm'):
                entity = await model.from_orms(item)
                # entity = model.from_orm(item)
                resp.append(entity)
    return resp

