from rest_framework import pagination


class MachinePaginator(pagination.PageNumberPagination):
    page_size = 10

class MachinePaginator(pagination.PageNumberPagination):
    page_size = 15

class UserPaginator(pagination.PageNumberPagination):
    page_size = 15

class MachineParameterValuePaginator(pagination.PageNumberPagination):
    page_size = 20

class MachineCategoryPaginator(pagination.PageNumberPagination):
    page_size = 10

class OperationPaginator(pagination.PageNumberPagination):
    page_size = 10

class MachineParameterPaginator(pagination.PageNumberPagination):
    page_size = 20

class RolePaginator(pagination.PageNumberPagination):
    page_size = 5