from typing import Type

from django.db.models import QuerySet
from logrich.logger_ import log  # noqa
from pydantic import BaseModel


async def get_qset(qset: QuerySet, model: Type[BaseModel]) -> list[BaseModel]:
    """get data from QuerySet"""
    # https://blog.etianen.com/blog/2013/06/08/django-querysets/
    resp = []
    if qset.aexists():
        async for item in qset.aiterator():
            if hasattr(model, "from_orms"):
                entity = await model.from_orms(item)
                resp.append(entity)
    return resp
