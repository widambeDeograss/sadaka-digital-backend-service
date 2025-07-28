from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from ..models import Revenue, PaymentType


class RevenueByPaymentTypeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, church_id):
        # Get the period from the request parameters, default to 'daily'
        period = request.query_params.get('period', 'daily').lower()

        # Get the current date and time
        now = timezone.now()

        # Define the start and end dates based on the period
        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(weeks=1)
        elif period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (start_date + timedelta(days=32)).replace(day=1)
        elif period == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            return Response({'error': 'Invalid period specified'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter revenues by church and date range
        revenues = Revenue.objects.filter(
            church_id=church_id,
            date_received__gte=start_date,
            date_received__lt=end_date
        )

        # Aggregate revenues by payment type
        revenue_summary = revenues.values('payment_type__name', "payment_type__id").annotate(
            total_amount=Sum('amount')
        ).order_by('payment_type__name')

        # Prepare the response data
        response_data = {
            'church_id': church_id,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'revenue_summary': list(revenue_summary)
        }

        return Response(response_data, status=status.HTTP_200_OK)