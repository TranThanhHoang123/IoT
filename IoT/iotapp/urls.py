from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'MachineCategory', views.MachineCategoryViewSet, basename='machinecategory')  # Specify the basename here
router.register(r'MachineParameter', views.MachineParameterViewSet, basename='machineparameter')  # Specify the basename here

urlpatterns = [
    path('', include(router.urls)),
]
