from fastapi import APIRouter, Depends
from starlette.exceptions import HTTPException as StarletteHTTPException

from database.crud_factory import PostCRUD, TopicCRUD
from database.db_conf import SessionLocal
from database.validation_schemas import (
    PostCreateValidatedData,
    PostUpdateValidatedData,
    TopicCreateValidatedData,
    TopicUpdateValidatedData,
)
from datastructures import (
    PageParams,
    PostData,
    RequesterData,
    TopicCreateData,
    TopicUpdateData,
)
from dependencies import JWTToken, get_db
from exceptions import NoPermissionException
from schemas import PaginatedResponse, PostSchema, TopicSchema
from utils import paginate

router = APIRouter(prefix="/api/forum", tags=["forum"])


jwt_token = JWTToken()


@router.get("/topics/")
async def topics(
    requester_data: RequesterData = Depends(jwt_token.decode),
    page_params: PageParams = Depends(),
    db: SessionLocal = Depends(get_db),
) -> PaginatedResponse[TopicSchema]:
    return paginate(page_params, TopicCRUD.get_many(db, order_by="created_on desc"))


@router.get("/topics/{topic_id}/")
async def topic_details(
    topic_id: int,
    requester_data: RequesterData = Depends(jwt_token.decode),
    db: SessionLocal = Depends(get_db),
) -> TopicSchema:
    return TopicCRUD.get_one(db, topic_id)


@router.post("/topics/")
async def topic_create(
    topic_data: TopicCreateData,
    requester_data: RequesterData = Depends(jwt_token.decode),
    db: SessionLocal = Depends(get_db),
) -> TopicSchema:
    validated_data = TopicCreateValidatedData(
        **topic_data.model_dump() | {"created_by": requester_data.name}
    )
    topic_obj = TopicCRUD.create(db, validated_data)
    return topic_obj


@router.patch("/topics/{topic_id}/")
async def topic_update(
    topic_id: int,
    topic_data: TopicUpdateData,
    requester_data: RequesterData = Depends(jwt_token.decode),
    db: SessionLocal = Depends(get_db),
) -> TopicSchema:
    if not set(requester_data.groups) & {"moderator"}:
        raise NoPermissionException(requester_data.name)
    topic_obj = TopicCRUD.get_one(db, topic_id)
    validated_data = TopicUpdateValidatedData(
        **topic_data.model_dump(exclude_none=True)
    )
    return TopicCRUD.update(db, topic_obj, validated_data)


@router.delete("/topics/{topic_id}/", response_model=bool)
async def topic_delete(
    topic_id: int,
    requester_data: RequesterData = Depends(jwt_token.decode),
    db: SessionLocal = Depends(get_db),
) -> bool | StarletteHTTPException:
    if not set(requester_data.groups) & {"moderator"}:
        raise NoPermissionException(requester_data.name)
    topic_obj = TopicCRUD.get_one(db, topic_id)
    return TopicCRUD.delete(db, topic_obj)


@router.get("/topics/{topic_id}/posts/")
async def topic_posts(
    topic_id: int,
    requester_data: RequesterData = Depends(jwt_token.decode),
    page_params: PageParams = Depends(),
    db: SessionLocal = Depends(get_db),
) -> PaginatedResponse[PostSchema]:
    return paginate(
        page_params,
        PostCRUD.get_many(db, topic_id, "topic_id", order_by="posted_on desc"),
    )


@router.post("/topics/{topic_id}/posts/")
async def topic_post_create(
    topic_id: int,
    post_data: PostData,
    requester_data: RequesterData = Depends(jwt_token.decode),
    db: SessionLocal = Depends(get_db),
) -> PostSchema:
    validated_data = PostCreateValidatedData(
        **post_data.model_dump(exclude_none=True)
        | {
            "author": requester_data.name,
            "topic_id": topic_id,
        }
    )
    return PostCRUD.create(db, validated_data)


@router.patch("/posts/{post_id}/")
async def topic_post_update(
    post_id: int,
    post_data: PostData,
    requester_data: RequesterData = Depends(jwt_token.decode),
    db: SessionLocal = Depends(get_db),
) -> PostSchema:
    post_obj = PostCRUD.get_one(db, post_id)
    if not (
        post_obj.author == requester_data.name
        or set(requester_data.groups) & {"moderator"}
    ):
        raise NoPermissionException(requester_data.name)
    validated_data = PostUpdateValidatedData(**post_data.model_dump(exclude_none=True))
    return PostCRUD.update(db, post_obj, validated_data)


@router.delete("/posts/{post_id}/")
async def topic_post_delete(
    post_id: int,
    requester_data: RequesterData = Depends(jwt_token.decode),
    db: SessionLocal = Depends(get_db),
) -> bool:
    post_obj = PostCRUD.get_one(db, post_id)
    if not (
        post_obj.author == requester_data.name
        or set(requester_data.groups) & {"moderator"}
    ):
        raise NoPermissionException(requester_data.name)
    return PostCRUD.delete(db, post_obj)
