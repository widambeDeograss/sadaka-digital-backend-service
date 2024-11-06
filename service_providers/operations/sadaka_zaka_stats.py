from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from datetime import datetime
from ..models import Zaka, Sadaka


class SadakaZakaStats(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query_type = request.query_params.get('type')
        church_id = request.query_params.get('church_id')
        if not church_id:
            return Response({"error": "church_id is required"}, status=400)

        today = timezone.now().date()
        current_year = today.year

        if query_type == 'sadaka_totals':
            return self.get_sadaka_totals(church_id, today, current_year)
        elif query_type == 'zaka_totals':
            return self.get_zaka_totals(church_id, today, current_year)
        elif query_type == 'zaka_sadaka':
            return self.get_area_chart_data(church_id, current_year)
        else:
            return Response({"error": "Invalid query type"}, status=400)

    def get_sadaka_totals(self, church_id, today, current_year):
        sadaka_cash_total = Sadaka.objects.filter(
            church_id=church_id,
            payment_type__name='Cash',
            date=today
        ).aggregate(total_cash=Sum('sadaka_amount'))['total_cash'] or 0

        sadaka_other_total = Sadaka.objects.filter(
            church_id=church_id,
            date=today
        ).exclude(
            payment_type__name='Cash'
        ).aggregate(total_other=Sum('sadaka_amount'))['total_other'] or 0

        sadaka_total_today = Sadaka.objects.filter(
            church_id=church_id,
            date=today
        ).aggregate(total_today=Sum('sadaka_amount'))['total_today'] or 0

        sadaka_total_year = Sadaka.objects.filter(
            church_id=church_id,
            date__year=current_year
        ).aggregate(total_year=Sum('sadaka_amount'))['total_year'] or 0

        return Response({
            "total_cash": sadaka_cash_total,
            "total_other": sadaka_other_total,
            "total_today": sadaka_total_today,
            "total_year": sadaka_total_year,
        })

    def get_zaka_totals(self, church_id, today, current_year):
        zaka_cash_total = Zaka.objects.filter(
            church_id=church_id,
            payment_type__name='Cash',
           date__year = current_year,
           date__month = today.month
        ).aggregate(total_cash=Sum('zaka_amount'))['total_cash'] or 0

        zaka_other_total = Zaka.objects.filter(
            church_id=church_id,
            date__year=current_year,
            date__month=today.month
        ).exclude(
            payment_type__name='Cash'
        ).aggregate(total_other=Sum('zaka_amount'))['total_other'] or 0

        zaka_total_today = Zaka.objects.filter(
            church_id=church_id,
            date__year=current_year,
            date__month=today.month
        ).aggregate(total_today=Sum('zaka_amount'))['total_today'] or 0

        zaka_total_year = Zaka.objects.filter(
            church_id=church_id,
            date__year=current_year
        ).aggregate(total_year=Sum('zaka_amount'))['total_year'] or 0

        return Response({
            "total_cash": zaka_cash_total,
            "total_other": zaka_other_total,
            "total_today": zaka_total_today,
            "total_year": zaka_total_year,
        })

    def get_area_chart_data(self, church_id, current_year):
        sadaka_monthly = (
            Sadaka.objects.filter(church_id=church_id, date__year=current_year)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('sadaka_amount'))
            .order_by('month')
        )

        zaka_monthly = (
            Zaka.objects.filter(church_id=church_id, date__year=current_year)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('zaka_amount'))
            .order_by('month')
        )

        # Initialize arrays with 0s for each month
        sadaka_data = [0] * 12
        zaka_data = [0] * 12

        # Populate data for each month
        for entry in sadaka_monthly:
            month_index = entry['month'].month - 1
            sadaka_data[month_index] = entry['total']

        for entry in zaka_monthly:
            month_index = entry['month'].month - 1
            zaka_data[month_index] = entry['total']

        # Prepare response in requested format
        area_chart_data = {
            "series": [
                {"name": "Sadaka", "data": sadaka_data, "offsetY": 0},
                {"name": "Zaka", "data": zaka_data, "offsetY": 0},
            ]
        }

        return Response(area_chart_data)
