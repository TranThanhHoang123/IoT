from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'MachineCategory', views.MachineCategoryViewSet, basename='machinecategory')  # Specify the basename here
router.register(r'MachineParameter', views.MachineParameterViewSet, basename='machineparameter')  # Specify the basename here
router.register(r'Machine', views.MachineViewSet, basename='machine')  # Specify the basename here
router.register(r'User', views.UserViewSet, basename='user')  # Specify the basename here
router.register(r'Operation', views.OperationViewSet, basename='operation')  # Specify the basename here
router.register(r'Values', views.MachineParameterValueViewSet, basename='values')  # Specify the basename here
router.register(r'data-history', views.MachineParameterValueHistoryViewSet, basename='data-history')  # Specify the basename here
urlpatterns = [
    path('', include(router.urls)),

]
