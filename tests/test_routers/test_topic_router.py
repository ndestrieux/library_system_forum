import json

import pytest

from tests.conftest import Users


class TestTopicList:
    @pytest.mark.parametrize(
        "override_jwt_token",
        [Users.TEST_BASIC_USER, Users.TEST_MODERATOR],
        indirect=True,
    )
    async def test_topic_list_when_request_sent_by_any_user_type_should_return_200(
        self, bulk_create_topics, async_test_client, db_session, override_jwt_token
    ):
        response = await async_test_client.get("/topics/")
        assert response.status_code == 200

    async def test_topic_list_when_request_sent_with_no_bearer_should_return_422(
        self, bulk_create_topics, async_test_client, db_session
    ):
        response = await async_test_client.get("/topics/")
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "override_jwt_token", [Users.TEST_BASIC_USER], indirect=True
    )
    async def test_topic_list_when_no_page_params_should_return_default(
        self, bulk_create_topics, async_test_client, db_session, override_jwt_token
    ):
        response = await async_test_client.get("/topics/")
        response_json = response.json()
        assert response_json["total"] == 20
        assert response_json["page"] == 1
        assert response_json["size"] == len(response_json["data"]) == 10

    @pytest.mark.parametrize(
        "override_jwt_token", [Users.TEST_BASIC_USER], indirect=True
    )
    async def test_topic_list_when_custom_page_params_should_return_correct_data(
        self, bulk_create_topics, async_test_client, db_session, override_jwt_token
    ):
        page_nb, page_size = 2, 5
        response = await async_test_client.get(
            "/topics/", params={"page": page_nb, "size": page_size}
        )
        response_json = response.json()
        assert response_json["page"] == page_nb
        assert response_json["size"] == len(response_json["data"]) == page_size

    @pytest.mark.parametrize(
        "override_jwt_token", [Users.TEST_BASIC_USER], indirect=True
    )
    async def test_topic_list_should_return_topics_ordered_by_created_on_date_descending(
        self, bulk_create_topics, async_test_client, db_session, override_jwt_token
    ):
        response = await async_test_client.get("/topics/")
        response_json = response.json()
        assert (
            response_json["data"][0]["created_on"]
            > response_json["data"][-1]["created_on"]
        )


class TestTopicDetails:
    @pytest.mark.parametrize(
        "override_jwt_token",
        [Users.TEST_BASIC_USER, Users.TEST_MODERATOR],
        indirect=True,
    )
    async def test_topic_details_when_request_sent_by_any_user_type_should_return_correct_object(
        self, bulk_create_topics, async_test_client, db_session, override_jwt_token
    ):
        response = await async_test_client.get("/topics/1/")
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["id"] == 1

    async def test_topic_details_when_request_sent_with_no_bearer_should_return_422(
        self, bulk_create_topics, async_test_client, db_session
    ):
        response = await async_test_client.get("/topics/1/")
        assert response.status_code == 422


class TestCreateTopic:
    @pytest.mark.parametrize(
        "override_jwt_token, requesting_user",
        [
            [Users.TEST_BASIC_USER for _ in range(2)],
            [Users.TEST_MODERATOR for _ in range(2)],
        ],
        indirect=["override_jwt_token"],
    )
    async def test_create_topic_when_request_sent_by_any_user_type_should_return_created_object(
        self, async_test_client, db_session, override_jwt_token, requesting_user
    ):
        data = {"title": "New topic", "category": "New category"}
        data_json = json.dumps(data)
        response = await async_test_client.post("/topics/", content=data_json)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["title"] == data["title"]
        assert response_json["category"] == data["category"]
        assert response_json["created_by"] == requesting_user

    async def test_create_topic_when_request_sent_with_no_bearer_should_return_422(
        self, async_test_client, db_session
    ):
        data = json.dumps({"title": "New topic", "category": "New category"})
        response = await async_test_client.post("/topics/", content=data)
        assert response.status_code == 422


class TestUpdateTopic:
    @pytest.mark.parametrize(
        "override_jwt_token, requesting_user, create_single_topic",
        [
            [Users.TEST_BASIC_USER for _ in range(3)],
            [Users.TEST_ANOTHER_BASIC_USER for _ in range(2)] + [Users.TEST_BASIC_USER],
        ],
        indirect=["override_jwt_token", "create_single_topic"],
    )
    async def test_update_topic_when_request_sent_by_any_basic_user_should_return_403(
        self,
        async_test_client,
        db_session,
        override_jwt_token,
        requesting_user,
        create_single_topic,
    ):
        data_json = json.dumps({"title": "Another topic actually"})
        response = await async_test_client.patch(
            f"/topics/{create_single_topic.id}/", content=data_json
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == f"User {requesting_user} does not have enough permission to perform this action!"
        )

    @pytest.mark.parametrize(
        "override_jwt_token, create_single_topic",
        [
            [Users.TEST_MODERATOR, Users.TEST_BASIC_USER],
            [Users.TEST_MODERATOR, Users.TEST_ANOTHER_MODERATOR],
            [Users.TEST_MODERATOR for _ in range(2)],
        ],
        indirect=["override_jwt_token", "create_single_topic"],
    )
    async def test_update_topic_when_moderator_updates_object_created_by_any_user_type_should_return_200(
        self, async_test_client, db_session, override_jwt_token, create_single_topic
    ):
        new_title = "Moderator changed topic title"
        data_json = json.dumps({"title": new_title})
        response = await async_test_client.patch(
            f"/topics/{create_single_topic.id}/", content=data_json
        )
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["title"] == new_title

    @pytest.mark.parametrize(
        "create_single_topic", [Users.TEST_BASIC_USER], indirect=["create_single_topic"]
    )
    async def test_update_topic_when_request_sent_with_no_bearer_should_return_422(
        self, async_test_client, db_session, create_single_topic
    ):
        data = json.dumps({"title": "Another topic actually"})
        response = await async_test_client.patch(
            f"/topics/{create_single_topic.id}/", content=data
        )
        assert response.status_code == 422


class TestDeleteTopic:
    @pytest.mark.parametrize(
        "override_jwt_token, requesting_user, create_single_topic",
        [
            [Users.TEST_BASIC_USER for _ in range(3)],
            [Users.TEST_ANOTHER_BASIC_USER for _ in range(2)] + [Users.TEST_BASIC_USER],
        ],
        indirect=["override_jwt_token", "create_single_topic"],
    )
    async def test_delete_topic_when_request_sent_by_any_basic_user_should_return_403(
        self,
        async_test_client,
        db_session,
        override_jwt_token,
        requesting_user,
        create_single_topic,
    ):
        response = await async_test_client.delete(f"/topics/{create_single_topic.id}/")
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == f"User {requesting_user} does not have enough permission to perform this action!"
        )

    @pytest.mark.parametrize(
        "override_jwt_token, create_single_topic",
        [
            [Users.TEST_MODERATOR, Users.TEST_BASIC_USER],
            [Users.TEST_MODERATOR, Users.TEST_ANOTHER_MODERATOR],
            [Users.TEST_MODERATOR for _ in range(2)],
        ],
        indirect=["override_jwt_token", "create_single_topic"],
    )
    async def test_delete_topic_when_moderator_deletes_object_created_by_any_user_type_should_return_200(
        self, async_test_client, db_session, override_jwt_token, create_single_topic
    ):
        response = await async_test_client.delete(f"/topics/{create_single_topic.id}/")
        assert response.status_code == 200
        assert response.json() is True
