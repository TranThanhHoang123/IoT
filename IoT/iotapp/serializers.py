from rest_framework import serializers
from .models import *


# Machine Category
# MachineCategorySerializer dùng để tạo và xóa chỉnh sửa
class MachineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineCategory
        fields = "__all__"


# MachineCategorySerializer dùng để lấy chi tiết của category
class MachineCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineCategory
        fields = "__all__"


# lấy danh sách category
class MachineCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineCategory
        fields = ["id", "name"]


# MachineParameterSerializer dùng để tạo và xóa chỉnh sửa
class MachineParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineParameter
        fields = "__all__"


# MachineCategorySerializer dùng để lấy detal của parameter
class MachineParameterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineParameter
        exclude = ['active', 'max_value', 'type']


# MachineCategorySerializer dùng để lấy list của parameter
class MachineParameterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineParameter
        fields = "__all__"


# MachineCategorySerializer dùng để lấy chi tiết của category
class MachineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ["ip", "id", "name", "image"]


# Tạo chỉnh sửa MachineSerializer
class MachineSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(default=True)

    class Meta:
        model = Machine
        fields = ['ip', 'active', 'image', 'id', 'name', 'parent', 'operation',
                  'category']


# chi tiết Machine
class MachineDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source="image")
    parent = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_parent(self, obj):
        if obj.parent:
            parent_serializer = MachineDetailSerializer(obj.parent, context=self.context)
            return parent_serializer.data
        return None

    def get_category(self, obj):
        if obj.category:
            category_serializer = MachineCategoryListSerializer(obj.category, context=self.context)
            return category_serializer.data
        return None

    def get_image(self, obj):
        if obj.image:
            # Lấy tên file hình ảnh từ đường dẫn được lưu trong trường image
            image_name = obj.image.name
            return self.context['request'].build_absolute_uri(f"/static/{image_name}")
        return None

    class Meta:
        model = Machine
        fields = "__all__"


# danh sách Machine
class MachineListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source="image")

    def get_image(self, obj):
        if obj.image:
            # Lấy tên file hình ảnh từ đường dẫn được lưu trong trường image
            image_name = obj.image.name
            return self.context['request'].build_absolute_uri(f"/static/{image_name}")
        return None

    class Meta:
        model = Machine
        exclude = ['parent', 'operation', 'category']


# tạo, chỉnh sửa vai trò
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']


# tạo, chỉnh sửa người dùng
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'email', 'image', 'role', 'phone_number', 'address']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data['password'])
        user.save()
        return user


# lấy thông tin người dùng
class UserDetailSerializer(UserSerializer):
    role = RoleSerializer()
    image = serializers.SerializerMethodField(source="image")

    def get_image(self, obj):
        if obj.image:
            # Lấy tên file hình ảnh từ đường dẫn được lưu trong trường image
            image_name = obj.image.name
            return self.context['request'].build_absolute_uri(f"/static/{image_name}")
        return None

    class Meta(UserSerializer.Meta):
        pass


# lấy danh sách người dùng
class UserListSerializer(UserDetailSerializer):
    role = RoleSerializer()

    class Meta(UserDetailSerializer.Meta):
        fields = ['id', 'name', 'email', 'image']


# thêm,sửa Nhà máy
class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['id', 'name', 'manager', 'city', 'district', 'address']


# tạo sửa giá trị thông số
class MachineParameterValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineParameterValue
        fields = '__all__'


# danh sách thông số
class MachineParameterValueListSerializer(serializers.ModelSerializer):
    parameter = serializers.SerializerMethodField()

    class Meta:
        model = MachineParameterValue
        fields = ['id', 'parameter', 'value']
    def get_parameter(self, obj):
        return {
            'id': obj.parameter.id,
            'name': obj.parameter.name,
            'unit_of_measurement': obj.parameter.unit_of_measurement
        }


class MachineValueSerializer(serializers.ModelSerializer):
    parameters = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = ['ip','id', 'name', 'parameters']

    def get_parameters(self, obj):
        parameter_values = MachineParameterValue.objects.filter(machine=obj)
        return MachineParameterValueListSerializer(parameter_values, many=True).data
