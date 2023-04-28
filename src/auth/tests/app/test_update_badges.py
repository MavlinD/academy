import pytest
from httpx import AsyncClient
from logrich.logger_ import log  # noqa

from src.auth.assets import update_badge

skip = False
# skip = True
reason = "Temporary off!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.local
async def test_update_badges(
    client: AsyncClient,
) -> None:
    """Тест обновления беджей"""
    content = "https://img.shields.io/badge/version-0.5.0-%230071C5?style=for-the-badge&logo=semver&logoColor=orange"
    result = await update_badge(search=r"\[version-badge\]: .*", content=f"[version-badge]: {content}")  # noqa
    response = result.find(content)
    assert response
