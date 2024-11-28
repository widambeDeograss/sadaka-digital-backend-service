from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, Q
from django.utils.timezone import now
from datetime import datetime

from service_providers.models import MavunoPayments


class MavunoStatsAndChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Single API for both totals and chart data.
        Use `type=totals` for totals or `type=chart` for chart data.
        Query params:
        - church_id: Required for both.
        - mavuno_id: Required for chart data (type=chart).
        - type: "totals" or "chart" (defaults to "totals").
        """
        # Extract query parameters
        query_type = request.query_params.get("type", "totals")  
        church_id = request.query_params.get("church_id")
        mavuno_id = request.query_params.get("mavuno_id")

        if not church_id:
            return Response({"error": "Church ID is required."}, status=400)

        # Handle totals
        if query_type == "totals":
            return self.get_totals(church_id)

        # Handle chart data
        if query_type == "chart":
            if not mavuno_id:
                return Response({"error": "Mavuno ID is required for chart data."}, status=400)
            return self.get_chart_data(mavuno_id)

        # Invalid query type
        return Response({"error": "Invalid type. Use 'totals' or 'chart'."}, status=400)

    def get_totals(self, church_id):
        """
        Calculate totals for Mavuno payments.
        """
        current_date = now()
        year = current_date.year
        month = current_date.month

        # Total payments this month
        total_payments_this_month = MavunoPayments.objects.filter(
            mavuno__church_id=church_id,
            inserted_at__year=year,
            inserted_at__month=month
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        # Total payments this year
        total_payments_this_year = MavunoPayments.objects.filter(
            mavuno__church_id=church_id,
            inserted_at__year=year
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        # Top-performing Jumuiya
        top_performing_jumuiya = (
            MavunoPayments.objects.filter(mavuno__church_id=church_id)
            .values(jumuiya_name=F('mavuno__jumuiya__name'))
            .annotate(total_collected=Sum('amount'))
            .order_by('-total_collected')
            .first()
        )

        # Response
        return Response({
            "stats": {
                "total_payments_this_month": total_payments_this_month,
                "total_payments_this_year": total_payments_this_year,
                "top_performing_jumuiya": top_performing_jumuiya or {"jumuiya_name": None, "total_collected": 0},
            }
        })

    def get_chart_data(self, mavuno_id):
        """
        Generate area chart data for a single Mavuno.
        """
        current_year = datetime.now().year

        # Aggregate payments by month
        monthly_data = (
            MavunoPayments.objects.filter(
                mavuno_id=mavuno_id,
                inserted_at__year=current_year
            )
            .annotate(month=F('inserted_at__month'))
            .values('month')
            .annotate(total_collected=Sum('amount'))
            .order_by('month')
        )

        # Ensure all months are represented (even if 0)
        monthly_totals = {month: 0 for month in range(1, 13)}
        for data in monthly_data:
            monthly_totals[data['month']] = data['total_collected']

        # Convert to list of dictionaries
        chart_data = [{"month": month, "total_collected": total} for month, total in monthly_totals.items()]

        # Response
        return Response({"chart_data": chart_data})
