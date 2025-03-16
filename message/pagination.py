from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    page_size = 10  # Limit messages per page to 10
    page_size_query_param = 'page_size'  # Allow clients to modify page size
    max_page_size = 50  # Prevent excessive data fetching
