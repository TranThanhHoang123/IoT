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


# Create your views here.
# View tạo chỉnh sửa User
class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, generics.RetrieveAPIView,
                  my_generics.NameSearch):
    queryset = User.objects.filter().all()
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]
    pagination_class = pagination.UserPaginator

    # phân quyền các chức năng
    def get_permissions(self):
        if self.action in ['current-user']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [my_permissions.IsAdmin()]
        return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        if self.action in ['list']:
            return UserListSerializer
        if self.action in ['retrieve']:
            return UserDetailSerializer
        return self.serializer_class

    @action(methods=['get'], url_path='current-user', detail=False)
    def current_user(self, request):
        return Response(UserDetailSerializer(request.user, context={"request": request}).data)


# View tạo,sửa,xóa MachineParameter và lấy detail của MachineParameter
class MachineParameterViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView,
                              generics.UpdateAPIView, my_generics.NameSearch):
    queryset = MachineParameter.objects.all().order_by("-created_date")
    serializer_class = MachineParameterSerializer
    pagination_class = pagination.MachineParameterPaginator

    def get_permissions(self):
        if self.action in ['list']:
            return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
        elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [my_permissions.IsAdmin()]
        return [my_permissions.IsAdmin()]

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
            return Response({"error": f"Không tìm thấy parameter có id: {kwargs.get('pk')}"},
                            status=status.HTTP_404_NOT_FOUND)


# View tạo,sửa,xóa MachineCategory và lấy detail của MachineCategory
class MachineCategoryViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, generics.RetrieveAPIView,
                             my_generics.NameSearch):
    queryset = MachineCategory.objects.all().order_by("-created_date")
    serializer_class = MachineCategorySerializer
    pagination_class = pagination.MachineCategoryPaginator

    def get_permissions(self):
        if self.action in ['list']:
            return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
        elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [my_permissions.IsAdmin()]
        return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        # khi lấy danh sách sẽ lấy MachineCategoryDetailSerializer nếu không thì sử dụng serializer của chính nó
        if self.action == 'list':
            return MachineCategoryDetailSerializer
        return self.serializer_class

    # Chỉnh sửa MachineCategory
    def update(self, request, *args, **kwargs):
        try:
            # Lấy id từ URL parameters
            id = kwargs.get('pk')

            # Lấy giá trị 'name' từ request data
            new_name = request.data.get('name', None)

            # Kiểm tra người dùng có gửi name lên không và name có rỗng hay không
            if not new_name:
                return Response({"error": "Tên danh mục không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

            # Xử lý chuỗi
            new_name = new_name.strip().lower()

            # Lấy đối tượng category dựa trên id
            # try:
            category = self.queryset.get(pk=id)
            # except MachineCategory.DoesNotExist:
            #     return Response({"error": f"Không tìm thấy loại máy nào có id: {id}"}, status=status.HTTP_404_NOT_FOUND)

            # Chuẩn bị dữ liệu để cập nhật
            data = {
                'name': new_name,
            }

            # Tiến hành serialize đối tượng category với dữ liệu đã chuẩn bị và partial=True để cho phép cập nhật một phần
            serializer = self.get_serializer(category, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Trả về thông tin chi tiết của đối tượng category sau khi cập nhật
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            if 'name' in e.detail and 'machine category with this name already exists.' in e.detail['name']:
                return Response({"error": f"Đã tồn tại danh mục có tên '{new_name}'"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except MachineCategory.DoesNotExist:
            return Response({"error": f"Không tìm thấy loại máy nào có id: {id}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # tạo MachineCategory
    def create(self, request, *args, **kwargs):
        name = request.data.get("name", None)

        # Kiểm tra nếu 'name' không tồn tại hoặc rỗng, trả về lỗi BadRequest
        if not name:
            return Response({"error": f"Tên danh mục không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

        # Xử lý chuỗi
        name = name.strip().lower()

        data = {
            'name': name,
        }

        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            if 'non_field_errors' in e.detail:
                return Response(
                    {"error": f"Đã tồn tại danh mục có tên '{name}'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    # lấy chi tiết một MachineCategory
    def retrieve(self, request, *args, **kwargs):
        try:
            category = self.get_object()  # Lấy đối tượng dựa trên kwargs['pk']
            serializer = MachineCategoryDetailSerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": f"Không tìm thấy đối tượng có id: {kwargs.get("pk")}"},
                            status=status.HTTP_404_NOT_FOUND)

    # lấy danh sách machine thuộc machine category
    @action(methods=['get'], url_path="machines", detail=True)
    def machines(self, request, pk):
        # Lấy danh sách các máy thuộc đối tượng MachineCategory có pk được cung cấp
        machines = self.get_object().machine_set.all().order_by('-created_date')

        # Serialize danh sách máy bằng MachineListSerializer và trả về dưới dạng JSON
        return Response(MachineListSerializer(machines, many=True).data, status=status.HTTP_200_OK)


class MachineViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, my_generics.NameSearch):
    queryset = Machine.objects.all().order_by("-created_date")
    serializer_class = MachineSerializer
    parser_classes = [MultiPartParser, ]
    pagination_class = pagination.MachinePaginator

    def get_permissions(self):
        if self.action in ['list','detail','sub_machine_values']:
            return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
        elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [my_permissions.IsAdmin()]
        return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        # khi lấy danh sách sẽ lấy MachineCategoryDetailSerializer nếu không thì sử dụng serializer của chính nó
        if self.action == 'list':
            return MachineListSerializer
        return self.serializer_class

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
    #lấy chi tiết của máy
    @action(methods=['get'], url_path="detail", detail=False)
    def get_detail(self, request):
        try:
            machine = Machine.objects.get(pk=request.data.get("ip"))
            serializer = MachineDetailSerializer(machine, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Machine.DoesNotExist:
            return Response({"error": "Máy không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

    #lấy danh sách máy con có trong máy chính
    @action(detail=False, methods=['get'], url_path='sub_machine_values')
    def sub_machine_values(self, request):
        machine = Machine.objects.get(ip=request.data.get('ip'))
        sub_machines = machine.sub_machines.all()
        serializer = MachineValueSerializer(sub_machines, many=True)
        return Response(serializer.data)



# Thêm chỉnh sửa Operation
class OperationViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.CreateAPIView, my_generics.NameSearch):
    queryset = Operation.objects.all().order_by('-created_date')
    serializer_class = OperationSerializer
    pagination_class = pagination.OperationPaginator

    def get_permissions(self):
        if self.action in ['list','machines','values']:
            return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
        elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [my_permissions.IsAdmin()]
        return [my_permissions.IsAdmin()]

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser or (user.role and user.role.name == "ADMIN"):
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(manager=user)
        #dùng lại phân trang
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Định nghĩa action để lấy tất cả các Machine thuộc về Operation
    @action(detail=True, methods=['get'], url_path='machines')
    def machines(self, request, pk=None):
        operation = self.get_object()  # Lấy đối tượng Operation từ pk
        machines = Machine.objects.filter(operation=operation,parent=None)
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data)

    # Lấy danh sách thông sô của machine cha thuộc Operation
    @action(detail=True, methods=['get'], url_path='values')
    def values(self, request, pk=None):
        operation = self.get_object()
        machines = Machine.objects.filter(operation=operation)
        serializer = MachineValueSerializer(machines, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Thêm, sửa thông số các giá trị
class MachineParameterValueViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView,
                                   my_generics.NameSearch):
    queryset = MachineParameterValue.objects.all().order_by('-created_date')
    serializer_class = MachineParameterValueSerializer
    pagination_class = pagination.MachineParameterValuePaginator

    def get_permissions(self):
        if self.action in ['list']:
            return [(my_permissions.IsKhachHang | my_permissions.IsAdmin)()]
        elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [my_permissions.IsAdmin()]
        return [my_permissions.IsAdmin()]

    def get_serializer_class(self):
        if self.action in ['list']:
            return MachineParameterValueListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)