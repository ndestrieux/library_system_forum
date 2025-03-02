from datetime import datetime, timedelta
from itertools import count
from typing import Dict, Iterator, List

import pytest
from freezegun import freeze_time

from database.models import Post, Topic


@pytest.fixture(scope="class")
def topic_data_list(get_faker, n: int = 20) -> List[Dict[str, str]]:
    fake = get_faker
    return [
        {
            "title": fake.sentence(),
            "category": fake.word(),
            "created_by": fake.first_name(),
        }
        for _ in range(n)
    ]


@pytest.fixture(scope="class")
def post_data_list(get_faker, n: int = 45) -> List[Dict[str, str]]:
    fake = get_faker
    return [
        {
            "content": fake.text(),
            "author": fake.first_name(),
        }
        for _ in range(n)
    ]


@pytest.fixture(scope="class")
def fake_dates() -> Iterator[datetime]:
    start_date = datetime(2020, 1, 1)
    return (start_date + timedelta(days=i) for i in count())


@pytest.fixture
def create_single_topic(request, get_faker, db_session, fake_dates) -> Topic:
    fake = get_faker
    created_by = request.param if hasattr(request, "param") else fake.first_name()
    with freeze_time(fake_dates):
        topic_obj = Topic(
            title=fake.sentence(), category=fake.word(), created_by=created_by
        )
        db_session.add(topic_obj)
        db_session.commit()
    return topic_obj


@pytest.fixture
def create_single_post(
    request, get_faker, create_single_topic, db_session, fake_dates
) -> Topic:
    fake = get_faker
    author = request.param if hasattr(request, "param") else fake.first_name()
    topic_obj = create_single_topic
    with freeze_time(fake_dates):
        post_obj = Post(content=fake.text(), author=author, topic_id=topic_obj.id)
        db_session.add(post_obj)
        db_session.commit()
    return post_obj


@pytest.fixture(scope="class")
def bulk_create_topics(db_session, topic_data_list, fake_dates) -> None:
    for data in topic_data_list:
        with freeze_time(fake_dates):
            db_session.add(Topic(**data))
            db_session.commit()


@pytest.fixture(scope="class")
def bulk_create_posts(db_session, topic_data_list, post_data_list, fake_dates) -> None:
    for i, topic_data in enumerate(topic_data_list[:3]):
        with freeze_time(fake_dates):
            topic_obj = Topic(**topic_data)
            db_session.add(topic_obj)
            db_session.commit()
        for post_data in post_data_list[i * 15 : i * 15 + 15]:
            with freeze_time(fake_dates):
                db_session.add(Post(**post_data | {"topic_id": topic_obj.id}))
                db_session.commit()
