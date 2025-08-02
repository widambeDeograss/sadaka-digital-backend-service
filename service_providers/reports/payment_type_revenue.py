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
        # church_id = request.query_params.get('church_id')
        period = request.query_params.get('period', 'daily').lower()
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')

        # Validate church_id is provided
        if not church_id:
            return Response(
                {'error': 'church_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If custom dates are provided, use them instead of period-based calculation
        if start_date_param and end_date_param:
            try:
                start_date = timezone.datetime.strptime(start_date_param, '%Y-%m-%d')
                end_date = timezone.datetime.strptime(end_date_param, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Calculate dates based on period if no custom dates provided
            now = timezone.now()

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
                return Response(
                    {'error': 'Invalid period specified. Use daily, weekly, monthly, or yearly'},
                    status=status.HTTP_400_BAD_REQUEST
                )
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