from rest_framework import generics, serializers
from datetime import datetime
from django.utils import timezone

# tìm theo trường tên
class NameSearch(generics.ListAPIView):
    queryset = None
    serializer_class = None

    # tìm theo tên
    def get_queryset(self):
        query = self.queryset
        kw = self.request.query_params.get('kw')
        if kw:
            query = query.filter(name__icontains=kw)
        return query


class MachineParameterValueHistorySearch(generics.ListAPIView):
    queryset = None
    serializer_class = None

    # tìm theo tên
    def get_queryset(self):
        queryset = self.queryset
        request = self.request
        # Lọc theo ngày tháng
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
                start_date = timezone.make_aware(start_date, timezone.get_default_timezone())
                queryset = queryset.filter(changed_date__gte=start_date)
            except ValueError:
                raise serializers.ValidationError({"error": "start_date không đúng định dạng YYYY-MM-DD."})
        if end_date:
            try:
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
                end_date = timezone.make_aware(end_date, timezone.get_default_timezone())
                queryset = queryset.filter(changed_date__lte=end_date)
            except ValueError:
                raise serializers.ValidationError({"error": "end_date không đúng định dạng YYYY-MM-DD."})

        # Lọc theo ip_machine
        machine_ip = request.query_params.get('machine_ip')
        if machine_ip:
            queryset = queryset.filter(machine_ip__icontains=machine_ip)

        # Lọc theo machine_name
        machine_name = request.query_params.get('machine_name')
        if machine_name:
            queryset = queryset.filter(machine_name__icontains=machine_name)

        return queryset


class OperationSearch(generics.ListAPIView):
    queryset = None
    serializer_class = None

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

        return query
