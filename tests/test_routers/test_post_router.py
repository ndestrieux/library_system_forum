import json

import pytest

from tests.conftest import Users


class TestPostList:
    @pytest.mark.parametrize(
        "override_jwt_token",
        [Users.TEST_BASIC_USER, Users.TEST_MODERATOR],
        indirect=True,
    )
    async def test_post_list_when_request_sent_by_any_user_type_should_return_200(
        self, bulk_create_posts, async_test_client, db_session, override_jwt_token
    ):
        response = await async_test_client.get("/topics/1/posts/")
        assert response.status_code == 200

    async def test_post_list_when_request_sent_with_no_bearer_should_return_422(
        self, bulk_create_posts, async_test_client, db_session
    ):
        response = await async_test_client.get("/topics/1/posts/")
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "override_jwt_token", [Users.TEST_BASIC_USER], indirect=True
    )
    async def test_post_list_when_no_page_params_should_return_default(
        self, bulk_create_posts, async_test_client, db_session, override_jwt_token
    ):
        response = await async_test_client.get("/topics/1/posts/")
        response_json = response.json()
        assert response_json["total"] == 15
        assert response_json["page"] == 1
        assert response_json["size"] == len(response_json["data"]) == 10

    @pytest.mark.parametrize(
        "override_jwt_token", [Users.TEST_BASIC_USER], indirect=True
    )
    async def test_post_list_when_custom_page_params_should_return_correct_data(
        self, bulk_create_posts, async_test_client, db_session, override_jwt_token
    ):
        page_nb, page_size = 2, 5
        response = await async_test_client.get(
            "/topics/1/posts/", params={"page": page_nb, "size": page_size}
        )
        response_json = response.json()
        assert response_json["page"] == page_nb
        assert response_json["size"] == len(response_json["data"]) == page_size

    @pytest.mark.parametrize(
        "override_jwt_token", [Users.TEST_BASIC_USER], indirect=True
    )
    async def test_post_list_should_return_posts_ordered_by_posted_on_date_descending(
        self, bulk_create_posts, async_test_client, db_session, override_jwt_token
    ):
        response = await async_test_client.get("/topics/1/posts/")
        response_json = response.json()
        assert (
            response_json["data"][0]["posted_on"]
            > response_json["data"][-1]["posted_on"]
        )


class TestCreatePost:
    @pytest.mark.parametrize(
        "override_jwt_token, requesting_user, post_data_list",
        [
            [Users.TEST_BASIC_USER for _ in range(2)] + [1],
            [Users.TEST_MODERATOR for _ in range(2)] + [1],
        ],
        indirect=["override_jwt_token", "post_data_list"],
    )
    async def test_create_post_when_request_sent_by_any_user_type_should_return_created_object(
        self,
        async_test_client,
        db_session,
        override_jwt_token,
        requesting_user,
        create_single_topic,
        post_data_list,
    ):
        topic_obj = create_single_topic
        data = post_data_list[0]
        data_json = json.dumps(data)
        response = await async_test_client.post(
            f"/topics/{topic_obj.id}/posts/", content=data_json
        )
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["content"] == data["content"]
        assert response_json["author"] == requesting_user

    async def test_create_post_when_request_sent_with_no_bearer_should_return_422(
        self, async_test_client, db_session
    ):
        data = json.dumps({"title": "New topic", "category": "New category"})
        response = await async_test_client.post("/topics/", content=data)
        assert response.status_code == 422


class TestUpdatePost:
    @pytest.mark.parametrize(
        "override_jwt_token, create_single_post",
        [
            [Users.TEST_MODERATOR, Users.TEST_BASIC_USER],
            [Users.TEST_BASIC_USER, Users.TEST_BASIC_USER],
            [Users.TEST_MODERATOR for _ in range(2)],
        ],
        indirect=["override_jwt_token", "create_single_post"],
    )
    async def test_update_post_when_moderator_or_author_updates_object_should_return_200(
        self,
        async_test_client,
        db_session,
        override_jwt_token,
        get_faker,
        create_single_post,
    ):
        fake = get_faker
        new_content = fake.text()
        data_json = json.dumps({"content": new_content})
        response = await async_test_client.patch(
            f"/posts/{create_single_post.id}/", content=data_json
        )
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["content"] == new_content

    @pytest.mark.parametrize(
        "override_jwt_token, requesting_user",
        [
            [Users.TEST_ANOTHER_BASIC_USER for _ in range(2)],
        ],
        indirect=["override_jwt_token"],
    )
    async def test_update_post_when_another_basic_user_updates_object_should_return_403(
        self,
        async_test_client,
        db_session,
        override_jwt_token,
        get_faker,
        requesting_user,
        create_single_post,
    ):
        fake = get_faker
        data_json = json.dumps({"content": fake.text()})
        response = await async_test_client.patch(
            f"/posts/{create_single_post.id}/", content=data_json
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == f"User {requesting_user} does not have enough permission to perform this action!"
        )

    @pytest.mark.parametrize(
        "create_single_post", [Users.TEST_BASIC_USER], indirect=["create_single_post"]
    )
    async def test_update_post_when_request_sent_with_no_bearer_should_return_422(
        self, async_test_client, db_session, create_single_post
    ):
        data = json.dumps({"title": "Another topic actually"})
        response = await async_test_client.patch(
            f"/posts/{create_single_post.id}/", content=data
        )
        assert response.status_code == 422


class TestPostDelete:
    @pytest.mark.parametrize(
        "override_jwt_token, create_single_post",
        [
            [Users.TEST_MODERATOR, Users.TEST_BASIC_USER],
            [Users.TEST_MODERATOR, Users.TEST_ANOTHER_MODERATOR],
            [Users.TEST_MODERATOR for _ in range(2)],
        ],
        indirect=["override_jwt_token", "create_single_post"],
    )
    async def test_delete_topic_when_moderator_or_author_deletes_object_should_return_200(
        self, async_test_client, db_session, override_jwt_token, create_single_post
    ):
        response = await async_test_client.delete(f"/posts/{create_single_post.id}/")
        assert response.status_code == 200
        assert response.json() is True

    @pytest.mark.parametrize(
        "override_jwt_token, requesting_user",
        [
            [Users.TEST_ANOTHER_BASIC_USER for _ in range(2)],
        ],
        indirect=["override_jwt_token"],
    )
    async def test_delete_post_when_another_basic_user_deletes_object_should_return_403(
        self,
        async_test_client,
        db_session,
        override_jwt_token,
        requesting_user,
        create_single_post,
    ):
        response = await async_test_client.delete(f"/posts/{create_single_post.id}/")
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == f"User {requesting_user} does not have enough permission to perform this action!"
        )
