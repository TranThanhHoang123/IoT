from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Machine)
admin.site.register(MachineParameter)
admin.site.register(MachineParameterValue)
admin.site.register(Operation)
admin.site.register(MachineCategory)