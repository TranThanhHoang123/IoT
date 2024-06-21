from rest_framework import serializers
from .models import *


# Machine Category
#MachineCategorySerializer dùng để tạo và xóa chỉnh sửa
class MachineCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = MachineCategory
        fields = ["name"]

#MachineCategorySerializer dùng để lấy chi tiết của category
class MachineCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineCategory
        fields = ["id","name"]


#MachineCategorySerializer dùng để tạo và xóa chỉnh sửa
class MachineParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = MachineCategory
        fields = ['id', 'name', 'unit_of_measurement', 'type', 'max_value']

#MachineCategorySerializer dùng để lấy chi tiết của category
class MachineParameterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineCategory
        exclude = ['active']


#MachineCategorySerializer dùng để lấy chi tiết của category
class MachineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ["ip","id","name","image"]


