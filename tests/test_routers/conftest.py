from datetime import datetime, timedelta
from itertools import count
from typing import Dict, Iterator, List

import pytest
from faker import Faker
from freezegun import freeze_time

from database.models import Topic


@pytest.fixture(scope="class")
def topic_data_list(n: int = 20) -> List[Dict[str, str]]:
    fake = Faker()
    return [
        {
            "title": fake.sentence(),
            "category": fake.word(),
            "created_by": fake.first_name(),
        }
        for _ in range(n)
    ]


@pytest.fixture(scope="class")
def fake_dates() -> Iterator[datetime]:
    start_date = datetime(2020, 1, 1)
    return (start_date + timedelta(days=i) for i in count())


@pytest.fixture(scope="class")
def bulk_create_topics(db_session, topic_data_list, fake_dates) -> None:
    for data in topic_data_list:
        with freeze_time(fake_dates):
            db_session.add(Topic(**data))
            db_session.commit()


@pytest.fixture
def create_single_topic(request, db_session) -> Topic:
    created_by = request.param
    fake = Faker()
    topic_obj = Topic(
        title=fake.sentence(), category=fake.word(), created_by=created_by
    )
    db_session.add(topic_obj)
    db_session.commit()
    return topic_obj
