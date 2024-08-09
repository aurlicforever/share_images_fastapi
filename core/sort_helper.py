from sqlalchemy.orm import Query
from sqlalchemy import text

class SortHelper:
    def apply_sort(self, query: Query, sort_by: str) -> Query:
        if not sort_by:
            return query
        return query.order_by(text(sort_by))
