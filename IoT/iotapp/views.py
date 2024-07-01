from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from rest_framework.exceptions import ValidationError
from . import my_generics, my_permissions, pagination
from django.core.exceptions import ObjectDoesNotExist
from .utils import *
from django.contrib.auth.hashers import make_password


# Create your views here.
# View tạo chỉnh sửa User
class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, generics.RetrieveAPIView,
                  my_generics.NameSearch):
    queryset = User.objects.filter().all().order_by('-created_date')
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]
    pagination_class = pagination.UserPaginator

    # phân quyền các chức năng
    # def get_permissions(self):
    #     if self.action in ['current-user']:
    #         return [permissions.IsAuthenticated()]
    #     elif self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy', 'customer',
    #                          'employee']:
    #         return [my_permissions.IsAdmin()]
    #     return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['list']:
            return UserListSerializer
        if self.action in ['retrieve']:
            return UserDetailSerializer
        return self.serializer_class

    @action(methods=['get'], url_path='current-user', detail=False)
    def current_user(self, request):
        return Response(UserDetailSerializer(request.user, context={"request": request}).data)

    # lấy danh sách khách hàng
    @action(methods=['get'], url_path='customers', detail=False)
    def customer(self, request):
        customers = User.objects.filter(role__name='KHACHHANG').order_by('-created_date')
        page = self.paginate_queryset(customers)
        if page is not None:
            serializer = UserListSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserListSerializer(customers, context={'request': request}, many=True)
        return Response(serializer.data)


    # lấy danh sách nhân viên
    @action(methods=['get'], url_path='employees', detail=False)
    def employee(self, request):
        employees = User.objects.filter(role__name='NHANVIEN').order_by('-created_date')
        page = self.paginate_queryset(employees)
        if page is not None:
            serializer = UserListSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserListSerializer(employees, context={'request': request}, many=True)
        return Response(serializer.data)

# View tạo,sửa,xóa MachineParameter và lấy detail của MachineParameter
class MachineParameterViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView,
                              generics.UpdateAPIView, my_generics.NameSearch):
    queryset = MachineParameter.objects.all().order_by("-created_date")
    serializer_class = MachineParameterSerializer
    pagination_class = pagination.MachineParameterPaginator

    # def get_permissions(self):
    #     if self.action in ['list']:
    #         return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
    #     elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
    #         return [my_permissions.IsAdmin()]
    #     return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        if self.action in ['list']:
            return MachineParameterListSerializer
        return self.serializer_class

    # tạo MachineParameter
    def create(self, request, *args, **kwargs):
        name = request.data.get('name', None)
        unit_of_measurement = request.data.get('unit_of_measurement', None)
        type = request.data.get('type', 'input')

        # Kiểm tra có trường name không
        if not name:
            return Response({"error": "Tên thông số không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra có trường unit_of_measurement không
        if not unit_of_measurement:
            return Response({"error": "Đơn vị thông số không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra có trường type có hợp lệ không
        if type not in ['input', 'output']:
            return Response({"error": "Giá trị của type phải là 'input' hoặc 'output'"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Xử lý chuỗi
        name = name.strip().lower()

        data = {
            'name': name,
            'unit_of_measurement': unit_of_measurement,
            'type': type,
            'max_value': request.data.get('max_value', None)
        }

        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            if 'non_field_errors' in e.detail:
                return Response(
                    {"error": f"Thông số {name} ({unit_of_measurement}) loại: {type} đã tồn tại."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    # Chỉnh sửa MachineParameter
    def update(self, request, *args, **kwargs):
        try:
            # Lấy id được gửi thông qua API
            id = kwargs.get('pk')

            # Lấy giá trị mới từ body
            name = request.data.get('name', None)
            unit_of_measurement = request.data.get('unit_of_measurement', None)
            type = request.data.get('type', 'input')

            # Kiểm tra người dùng có gửi name lên không và name có trống hay không
            if not name:
                return Response({"error": "Tên thông số không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra người dùng có gửi unit_of_measurement lên không và unit_of_measurement có trống hay không
            if not unit_of_measurement:
                return Response({"error": "Đơn vị thông số không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra giá trị của type có hợp lệ không
            if type not in ['input', 'output']:
                return Response({"error": "Giá trị của type phải là 'input' hoặc 'output'"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Xử lý chuỗi
            name = name.strip().lower()

            # Kiểm tra xem có tồn tại parameter cần sửa không
            parameter = MachineParameter.objects.get(pk=id)

            # Chuẩn bị dữ liệu để cập nhật
            data = {
                'name': name,
                'unit_of_measurement': unit_of_measurement,
                'type': type,
                'max_value': request.data.get('max_value', parameter.max_value)
                # Giữ nguyên giá trị cũ nếu không có giá trị mới
            }

            # Tiến hành serialize và cập nhật đối tượng
            serializer = self.get_serializer(parameter, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Trả về đối tượng đã cập nhật
            return Response(MachineParameterDetailSerializer(parameter).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            if 'non_field_errors' in e.detail:
                return Response(
                    {"error": f"Thông số '{name} ({unit_of_measurement}) loại: {type}' đã tồn tại."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except MachineParameter.DoesNotExist:
            return Response({"error": f"Không tìm thấy thông số nào nào có id: {id}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            parameter = self.get_object()  # Lấy đối tượng dựa trên kwargs['pk']
            serializer = MachineParameterDetailSerializer(parameter)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": f"Không tìm thấy parameter"}, status=status.HTTP_404_NOT_FOUND)


# View tạo,sửa,xóa MachineCategory và lấy detail của MachineCategory
class MachineCategoryViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, generics.RetrieveAPIView,
                             my_generics.NameSearch):
    queryset = MachineCategory.objects.all().order_by("-created_date")
    serializer_class = MachineCategorySerializer
    pagination_class = pagination.MachineCategoryPaginator

    # def get_permissions(self):
    #     if self.action in ['list']:
    #         return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
    #     elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
    #         return [my_permissions.IsAdmin()]
    #     return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        # khi lấy danh sách sẽ lấy MachineCategoryDetailSerializer nếu không thì sử dụng serializer của chính nó
        if self.action == 'list':
            return MachineCategoryDetailSerializer
        return self.serializer_class

    # Chỉnh sửa MachineCategory
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except MachineCategory.DoesNotExist:
            return Response({"error": "Machine Category không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            errors = dict(e.detail)
            error_response = {}

            if 'name' in errors and errors['name'][0].code == 'blank':
                error_response['name'] = "Tên thông số không được để trống"
            if 'name' in errors and errors['name'][0].code == 'unique':
                error_response['name'] = f"Đã tồn tại tên loại máy có tên: {request.data.get('name')}"

            if error_response:
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # tạo MachineCategory
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            response_serializer = MachineCategoryDetailSerializer(instance, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            errors = dict(e.detail)
            error_response = {}

            if 'name' in errors and errors['name'][0].code == 'blank':
                error_response['name'] = "Tên thông số không được để trống"
            if 'name' in errors and errors['name'][0].code == 'unique':
                error_response['name'] = f"Đã tồn tại máy có tên này: {request.data.get('name')}"

            if error_response:
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


    # lấy chi tiết một MachineCategory
    def retrieve(self, request, *args, **kwargs):
        try:
            category = self.get_object()  # Lấy đối tượng dựa trên kwargs['pk']
            serializer = MachineCategoryDetailSerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": f"Không tìm thấy machine category"},
                            status=status.HTTP_404_NOT_FOUND)

    # lấy danh sách machine thuộc machine category
    @action(methods=['get'], url_path="machines", detail=True)
    def machines(self, request, pk):
        # Lấy danh sách các máy thuộc đối tượng MachineCategory có pk được cung cấp
        machines = self.get_object().machine_set.all().order_by('-created_date')
        page = self.paginate_queryset(machines)
        if page is not None:
            serializer = MachineListSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MachineListSerializer(machines, context={'request': request}, many=True)
        return Response(serializer.data)


class MachineViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, my_generics.NameSearch):
    queryset = Machine.objects.all().order_by("-created_date")
    serializer_class = MachineSerializer
    parser_classes = [MultiPartParser, ]
    pagination_class = pagination.MachinePaginator

    # def get_permissions(self):
    #     if self.action in ['list', 'detail', 'sub_machine_values']:
    #         return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
    #     elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
    #         return [my_permissions.IsAdmin()]
    #     return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        # khi lấy danh sách sẽ lấy MachineCategoryDetailSerializer nếu không thì sử dụng serializer của chính nó
        if self.action == 'list':
            return MachineValueSerializer
        return self.serializer_class
    # tạo machine
    def create(self, request, *args, **kwargs):
        serializer = MachineSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            response_serializer = MachineDetailSerializer(instance, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            errors = dict(e.detail)
            error_response = {}

            if 'operation' in errors and errors['operation'][0].code == 'does_not_exist':
                error_response['operation'] = f"Id mô hình {request.data.get('operation')} không hợp lệ"
            if 'parent' in errors and errors['parent'][0].code == 'does_not_exist':
                error_response['parent'] = f"Ip máy {request.data.get('parent')} không hợp lệ"
            if 'category' in errors and errors['category'][0].code == 'does_not_exist':
                error_response['category'] = f"Danh mục không hợp lệ"
            if 'ip' in errors and errors['ip'][0].code == 'blank':
                error_response['ip'] = "Ip thông số không được để trống"
            if 'name' in errors and errors['name'][0].code == 'blank':
                error_response['name'] = "Tên thông số không được để trống"
            if 'id' in errors and errors['id'][0].code == 'blank':
                error_response['id'] = "Id thông số không được để trống"
            if 'ip' in errors and errors['ip'][0].code == 'unique':
                error_response['ip'] = f"Đã tồn tại máy có ip: {request.data.get('ip')}"
            if 'id' in errors and errors['id'][0].code == 'unique':
                error_response['id'] = f"Đã tồn tại máy có id: {request.data.get('id')}"

            if error_response:
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # update Machine
    def update(self, request, *args, **kwargs):
        try:
            instance = Machine.objects.get(ip=request.data.get("ip"))
        except Machine.DoesNotExist:
            return Response({"error": "Máy không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Sử dụng serializer khác để trả về phản hồi
            response_serializer = MachineDetailSerializer(instance, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            errors = dict(e.detail)
            error_response = {}

            if 'operation' in errors and errors['operation'][0].code == 'does_not_exist':
                error_response['operation'] = f"Id nhà máy {request.data.get('operation')} không hợp lệ"
            if 'parent' in errors and errors['parent'][0].code == 'does_not_exist':
                error_response['parent'] = f"Ip máy {request.data.get('parent')} không hợp lệ"
            if 'category' in errors and errors['category'][0].code == 'does_not_exist':
                error_response['category'] = f"Danh mục không hợp lệ"
            if 'ip' in errors and errors['ip'][0].code == 'blank':
                error_response['ip'] = "Ip thông số không được để trống"
            if 'name' in errors and errors['name'][0].code == 'blank':
                error_response['name'] = "Tên thông số không được để trống"
            if 'id' in errors and errors['id'][0].code == 'blank':
                error_response['id'] = "Id thông số không được để trống"
            if 'ip' in errors and errors['ip'][0].code == 'unique':
                error_response['ip'] = f"Đã tồn tại máy có ip: {request.data.get('ip')}"
            if 'id' in errors and errors['id'][0].code == 'unique':
                error_response['id'] = f"Đã tồn tại máy có id: {request.data.get('id')}"

            if error_response:
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # lấy chi tiết của máy
    @action(methods=['get'], url_path="detail", detail=False)
    def get_detail(self, request):
        try:
            machine = Machine.objects.get(pk=request.data.get("ip"))
            serializer = MachineValueSerializer(machine, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Machine.DoesNotExist:
            return Response({"error": "Máy không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

    # lấy danh sách máy con có trong máy chính kem thong so
    @action(detail=False, methods=['get'], url_path='sub_machine_values')
    def sub_machine_values(self, request):
        machine = Machine.objects.get(ip=request.data.get('ip'))
        sub_machines = machine.sub_machines.all().order_by('-created_date')
        page = self.paginate_queryset(sub_machines)
        if page is not None:
            serializer = MachineValueSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MachineValueSerializer(sub_machines, many=True)
        return Response(serializer.data)

    # lay danh sachs may chinh kem thong so cua no
    @action(detail=False, methods=['get'], url_path='main_machine_values')
    def main_machine_values(self, request):
        machines = Machine.objects.filter(parent=None).order_by('-created_date')
        page = self.paginate_queryset(machines)
        if page is not None:
            serializer = MachineValueSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MachineValueSerializer(machines, many=True)
        return Response(serializer.data)


# Thêm chỉnh sửa Operation
class OperationViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.CreateAPIView, generics.ListAPIView,generics.RetrieveAPIView):
    queryset = Operation.objects.all().order_by('-created_date')
    serializer_class = OperationSerializer
    pagination_class = pagination.OperationPaginator
    # def get_permissions(self):
    #     if self.action in ['list', 'machines', 'values']:
    #         return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
    #     elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
    #         return [my_permissions.IsAdmin()]
    #     return [my_permissions.IsAdmin()]

    def get_queryset(self):
        query = self.queryset
        kw = self.request.query_params.get('kw')
        city = self.request.query_params.get('city')
        district = self.request.query_params.get('district')

        if kw:
            query = query.filter(name__icontains=kw)
        if city:
            query = query.filter(city__icontains=city)
        if district:
            query = query.filter(district__icontains=district)
        user = self.request.user

        if user.is_superuser or (user.role and user.role.name == "ADMIN"):
            query = query
        else:
            query = query.filter(manager=user)
        return query

    # Định nghĩa action để lấy tất cả các Machine thuộc về Operation
    @action(detail=True, methods=['get'], url_path='machines')
    def machines(self, request, pk=None):
        operation = self.get_object()  # Lấy đối tượng Operation từ pk
        machines = Machine.objects.filter(operation=operation, parent=None)
        page = self.paginate_queryset(machines)
        if page is not None:
            serializer = MachineValueSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MachineValueSerializer(machines, many=True)
        return Response(serializer.data)


    # Lấy danh sách thông sô của machine cha thuộc Operation
    @action(detail=True, methods=['get'], url_path='values')
    def values(self, request, pk=None):
        operation = self.get_object()
        machines = Machine.objects.filter(operation=operation)
        page = self.paginate_queryset(machines)
        if page is not None:
            serializer = MachineValueSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MachineValueSerializer(machines, many=True)
        return Response(serializer.data)
    #tạo operation
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            response_serializer = OperationDetailSerializer(instance, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            errors = dict(e.detail)
            error_response = {}

            if 'name' in errors and errors['name'][0].code == 'blank':
                error_response['name'] = "Tên nhà máy không được để trống"

            if error_response:
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    #update operation
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Operation.DoesNotExist:
            return Response({"error": "Nhà máy không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            errors = dict(e.detail)
            error_response = {}

            if 'manager' in errors and errors['manager'][0].code == 'does_not_exist':
                error_response['manager'] = f"id manager {request.data.get('manager')} không hợp lệ"
            if 'name' in errors and errors['name'][0].code == 'blank':
                error_response['name'] = "Tên thông số không được để trống"

            if error_response:
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


# Thêm, sửa thông số các giá trị
class MachineParameterValueViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView,
                                   generics.ListAPIView):
    queryset = MachineParameterValue.objects.all().order_by('-created_date')
    serializer_class = MachineParameterValueSerializer
    pagination_class = pagination.MachineParameterValuePaginator

    # def get_permissions(self):
    #     if self.action in ['list']:
    #         return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
    #     elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
    #         return [my_permissions.IsAdmin()]
    #     return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        if self.action in ['list']:
            return MachineParameterValueListSerializer
        return self.serializer_class

    #tạo machineparametervalue
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            errors = dict(e.detail)
            error_response = {}

            if 'machine' in errors and errors['machine'][0].code == 'does_not_exist':
                error_response['machine'] = f"Id máy {request.data.get('machine')} không hợp lệ"
            if 'parameter' in errors and errors['parameter'][0].code == 'does_not_exist':
                error_response['parameter'] = f"Ip thông số {request.data.get('parameter')} không hợp lệ"
            if error_response:
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_value = instance.value
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        activity_level = 'Normal'
        # Check if the new value is greater than or equal to the max value
        new_value = serializer.validated_data.get('value')
        if instance.parameter.max_value and new_value >= instance.parameter.max_value:
            activity_level = 'Critical'

        # Check if the updated_date is at least 1 minute apart from old_updated_date
        if (instance.updated_history_date is None or is_updated_date_within_minutes(instance.updated_history_date,
                                                                                    1)) or (
                activity_level == 'Critical'):
            # Create a MachineParameterValueHistory record
            MachineParameterValueHistory.objects.create(
                machine_ip=instance.machine.ip,
                machine_name=instance.machine.name,
                parameter_name=instance.parameter.name,
                unit_of_measurement=instance.parameter.unit_of_measurement,
                old_value=old_value,
                new_value=serializer.validated_data.get('value'),
                activity_level=activity_level,
                changed_date=instance.updated_history_date  # Use updated_history_date for history
            )
            # Update updated_history_date to current updated_date
            instance.updated_history_date = instance.updated_date

        # Save the instance after creating history
        instance.save()

        return Response(serializer.data)


class MachineParameterValueHistoryViewSet(viewsets.ViewSet, my_generics.MachineParameterValueHistorySearch):
    serializer_class = MachineParameterValueHistorySerializer
    queryset = MachineParameterValueHistory.objects.all().order_by('-changed_date')
    pagination_class = pagination.HistoryDataPaginator