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


class MachineCategory(BaseModel):
    name = models.CharField(max_length=40, unique=True)  # tên vai trò phải là unique
    def __str__(self):
        return self.name


# Người dùng
class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = None  # Không sử dụng trường first_name của AbstractUser
    last_name = None  # Không sử dụng trường last_name của AbstractUser
    address = models.CharField(max_length=50, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='User/%Y/%m', blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=150, null=True)# tên của khách hàng thuê
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name}"


#các máy móc
class Machine(BaseModel):
    ip = models.CharField(max_length=16, primary_key=True)  # Khóa chính, kiểu chuỗi
    id = models.CharField(max_length=30,unique=True,null=True)
    name = models.CharField(max_length=40)  # Tên máy, kiểu chuỗi
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_machines')
    image = models.ImageField(upload_to='Machine/%Y/%m', blank=True, null=True)
    operation = models.ForeignKey('Operation', on_delete=models.SET_NULL, null=True, blank=True, related_name='machines')
    category = models.ForeignKey(MachineCategory,on_delete=models.PROTECT,null=True)

    def __str__(self):
        return f"{self.name} ({self.ip})"


#thống số máy
class MachineParameter(BaseModel):
    INPUT = 'input'
    OUTPUT = 'output'
    PARAMETER_TYPES = [
        (INPUT, 'Input'),
        (OUTPUT, 'Output'),
    ]
    name = models.CharField(max_length=30)  # Tên tham số, kiểu chuỗi
    unit_of_measurement = models.CharField(max_length=10)  # Đơn vị đo lường, kiểu chuỗi
    type = models.CharField(max_length=6, choices=PARAMETER_TYPES, default=INPUT)  # Loại tham số: đầu vào hoặc đầu ra
    max_value = models.FloatField(null=True)  # Mức tối đa cho chỉ số

    class Meta:
        unique_together = ('name', 'unit_of_measurement','type')

    def __str__(self):
        return f"{self.name} ({self.unit_of_measurement})"


class MachineParameterValue(BaseModel):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)  # Khóa ngoại tới Machine, khi Machine bị xóa thì dòng này cũng bị xóa
    parameter = models.ForeignKey(MachineParameter, on_delete=models.CASCADE)  # Khóa ngoại tới MachineParameter, khi MachineParameter bị xóa thì dòng này cũng bị xóa
    value = models.FloatField(null=True)  # Giá trị của tham số
    updated_history_date = models.DateTimeField(null=True)
    class Meta:
        unique_together = ('machine', 'parameter')  # Đảm bảo mỗi máy chỉ có một giá trị cho mỗi tham số

    def __str__(self):
        return f"{self.machine.name}({self.parameter.name}): {self.value} {self.parameter.unit_of_measurement}"


class Operation(BaseModel):
    name = models.CharField(max_length=30)
    manager = models.ForeignKey('User', on_delete=models.SET_NULL,null=True,blank=True, related_name='operations') # Một operation có một manager hoặc không khi User bị xóa thì manager = null User có thể truy vấn Operation thông qua related_name = operations
    city = models.CharField(max_length=15, blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=180, blank=True, null=True)

    def __str__(self):
        return self.name


class MachineParameterValueHistory(models.Model):
    machine_ip = models.CharField(max_length=16)
    machine_name = models.CharField(max_length=40)
    parameter_name = models.CharField(max_length=30)
    unit_of_measurement = models.CharField(max_length=10)
    old_value = models.FloatField(null=True)
    new_value = models.FloatField(null=True)
    changed_date = models.DateTimeField(auto_now_add=True)
    ACTIVITY_LEVELS = [
        ('Normal', 'Bình thường'),
        ('Warning', 'Cảnh báo'),
        ('Critical', 'Nguy hiểm'),
    ]
    activity_level = models.CharField(max_length=10, choices=ACTIVITY_LEVELS, default='Normal')

    def __str__(self):
        return f"History of {self.machine_name}({self.ip_machine})({self.parameter_name}) from {self.old_value} to {self.new_value} on {self.changed_date}"
