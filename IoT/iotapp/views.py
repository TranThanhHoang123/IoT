from django.shortcuts import render
from rest_framework import viewsets, generics, status
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404


# Create your views here.


#View tạo,sửa,xóa MachineParameter và lấy detail của MachineParameter
class MachineParameterViewSet(viewsets.ViewSet,generics.ListAPIView,generics.RetrieveAPIView):
    queryset = MachineParameter.objects.all().order_by("-created_date")
    serializer_class = MachineParameterSerializer

    def get_serializer_class(self):
        if self.action in ['list']:
            return MachineParameterDetailSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        try:
            parameter = self.get_object()  # Lấy đối tượng dựa trên kwargs['pk']
            serializer = MachineParameterDetailSerializer(parameter)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": f"Không tìm thấy parameter có id: {kwargs.get("pk")}"}, status=status.HTTP_404_NOT_FOUND)

# View tạo,sửa,xóa MachineCategory và lấy detail của MachineCategory
class MachineCategoryViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = MachineCategory.objects.all().order_by("-created_date")
    serializer_class = MachineCategorySerializer

    def get_serializer_class(self):
        # khi lấy danh sách sẽ lấy MachineCategoryDetailSerializer nếu không thì sử dụng serializer của chính nó
        if self.action == 'list':
            return MachineCategoryDetailSerializer
        return self.serializer_class
    #chỉnh sửa MachineCategory
    def update(self, request, *args, **kwargs):
        try:
            # Lấy id được gửi thông qua API từ kwargs
            id = kwargs.get('pk')

            # Lấy giá trị name được gửi từ body request
            new_name = request.data.get('name', None)

            # Kiểm tra người dùng có gửi name lên không và name có rỗng hay không
            if not new_name:
                return Response({"error": f"Tên danh mục không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

            # Lấy đối tượng category dựa trên id từ cơ sở dữ liệu
            category = self.get_object()

            # Kiểm tra xem tên danh mục mới đã tồn tại chưa
            if self.queryset.exclude(pk=category.pk).filter(name=new_name).exists():
                return Response({"error": f"Đã tồn tại danh mục có tên '{new_name}'"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Tiến hành serialize đối tượng category với dữ liệu từ request và partial=True để cho phép chỉnh sửa một phần
            serializer = self.get_serializer(category, data=request.data, partial=True)

            # Kiểm tra tính hợp lệ của dữ liệu từ serializer, nếu không hợp lệ sẽ ném ra một exception
            serializer.is_valid(raise_exception=True)

            # Thực hiện cập nhật đối tượng category trong cơ sở dữ liệu
            self.perform_update(serializer)

            # Trả về thông tin chi tiết của đối tượng category sau khi cập nhật
            return Response(MachineCategoryDetailSerializer(category).data)

        except MachineCategory.DoesNotExist:
            return Response({"error": f"Không tìm thấy loại máy nào có id: {id}"}, status=status.HTTP_404_NOT_FOUND)
    #tạo MachineCategory
    def create(self, request, *args, **kwargs):
        # Lấy giá trị 'name' từ dữ liệu gửi lên
        name = request.data.get("name", None)

        # Kiểm tra nếu 'name' không tồn tại hoặc rỗng, trả về lỗi BadRequest
        if not name:
            return Response({"error": f"Tên danh mục không được để trống"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra xem đã tồn tại danh mục với 'name' đã được gửi lên chưa
        if self.queryset.filter(name=name).exists():
            return Response({"error": f"Đã tồn tại danh mục có tên '{name}'"}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo serializer dựa trên dữ liệu gửi lên
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Lưu đối tượng mới tạo vào cơ sở dữ liệu
        self.perform_create(serializer)

        # Trả về thông tin chi tiết của đối tượng vừa tạo dưới dạng JSON
        return Response(MachineCategoryDetailSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)

    #lấy chi tiết một MachineCategory
    def retrieve(self, request, *args, **kwargs):
        try:
            category = self.get_object()  # Lấy đối tượng dựa trên kwargs['pk']
            serializer = MachineCategoryDetailSerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": f"Không tìm thấy đối tượng có id: {kwargs.get("pk")}"}, status=status.HTTP_404_NOT_FOUND)


    #lấy danh sách machine thuộc machine category
    @action(methods=['get'], url_path="machines", detail=True)
    def machines(self, request, pk):
        # Lấy danh sách các máy thuộc đối tượng MachineCategory có pk được cung cấp
        machines = self.get_object().machine_set.filter(active=True).all()

        # Serialize danh sách máy bằng MachineListSerializer và trả về dưới dạng JSON
        return Response(MachineListSerializer(machines, many=True).data, status=status.HTTP_200_OK)