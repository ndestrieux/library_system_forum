from datastructures import PageParams
from schemas import PaginatedResponse, T


def paginate(page_params: PageParams, query) -> PaginatedResponse[T]:
    """
    Paginate the results of a query.

    Args:
        page_params (PageParams): The pagination parameters, including page number and size.
        query (Query): The SQLAlchemy query to paginate.

    Returns:
        PaginatedResponse[T]: A paginated response containing the total count,
        current page, page size, and the data for the current page.
    """
    paginated_query = (
        query.offset((page_params.page - 1) * page_params.size)
        .limit(page_params.size)
        .all()
    )
    return PaginatedResponse(
        total=query.count(),
        page=page_params.page,
        size=page_params.size,
        data=paginated_query,
    )
