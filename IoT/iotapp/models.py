from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


#model này chứa các dữ liệu dùng dung cho các model khác
class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True,null=True)
    updated_date = models.DateTimeField(auto_now=True,null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

#model này đại diện cho vai trò của User
class Role(BaseModel):
    name = models.CharField(max_length=20, unique=True)#tên vai trò phải là unique

    def __str__(self):
        return self.name


# Người dùng
class User(AbstractUser):
    citizen_identification = models.CharField(max_length=20, blank=True, null=True,unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=180, blank=True, null=True)
    role = models.OneToOneField(Role, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='User/%Y/%m', blank=True, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


#các máy móc
class Machine(BaseModel):
    ip = models.CharField(max_length=16, primary_key=True)  # Khóa chính, kiểu chuỗi
    id = models.CharField(max_length=30,unique=True,null=True)
    name = models.CharField(max_length=40)  # Tên máy, kiểu chuỗi
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_machines')
    image = models.ImageField(upload_to='Machine/%Y/%m', blank=True, null=True)
    operation = models.ForeignKey('Operation', on_delete=models.SET_NULL, null=True, blank=True, related_name='machines')


#thống số máy
class MachineParameter(BaseModel):
    name = models.CharField(max_length=30, unique = True)  # Tên tham số, kiểu chuỗi
    unit_of_measurement = models.CharField(max_length=10)  # Đơn vị đo lường, kiểu chuỗi


class MachineParameterValue(BaseModel):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)  # Khóa ngoại tới Machine, khi Machine bị xóa thì dòng này cũng bị xóa
    parameter = models.ForeignKey(MachineParameter, on_delete=models.CASCADE)  # Khóa ngoại tới MachineParameter, khi MachineParameter bị xóa thì dòng này cũng bị xóa
    value = models.FloatField()  # Giá trị của tham số

    class Meta:
        unique_together = ('machine', 'parameter')  # Đảm bảo mỗi máy chỉ có một giá trị cho mỗi tham số


class Operation(BaseModel):
    name = models.CharField(max_length=30)
    manager = models.ForeignKey('User', on_delete=models.SET_NULL,null=True,blank=True, related_name='operations') # Một operation có một manager hoặc không khi User bị xóa thì manager = null User có thể truy vấn Operation thông qua related_name = operations

    def __str__(self):
        return self.name
