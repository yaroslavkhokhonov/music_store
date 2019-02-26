from flask_restful import reqparse

from flaskr.settings import DEFAULT_PAGE_SIZE


def with_pagination(func):
    """
    Decorator for adding pagination kwargs for resource view.
    """

    def wrapper(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('page_size', type=int, default=DEFAULT_PAGE_SIZE)
        parser.add_argument('page', type=int)
        kwargs.update(parser.parse_args())
        return func(*args, **kwargs)

    return wrapper
