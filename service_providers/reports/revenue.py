from django.db import connection
from django.http import JsonResponse
from django.views import View
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from calendar import monthrange
import json

from rest_framework.permissions import IsAuthenticated


class RevenueReportView(View):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            # Get parameters from request
            church_id = request.GET.get('church_id')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            # If no dates provided, default to current month
            if not start_date or not end_date:
                today = timezone.now().date()
                start_date = date(today.year, today.month, 1)
                _, last_day = monthrange(today.year, today.month)
                end_date = date(today.year, today.month, last_day)
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Base query
            query = """
                SELECT 
                    revenue_type,
                    revenue_type_record,
                    payment_type_name,
                    SUM(amount) as total_amount,
                    month_name,
                    year
                FROM church_revenue_view
                WHERE transaction_date BETWEEN %s AND %s
            """

            params = [start_date, end_date]

            # Add church_id filter if provided
            if church_id:
                query += " AND church_id = %s"
                params.append(church_id)

            # Group by and order by
            query += """
                GROUP BY 
                    revenue_type,
                    revenue_type_record,
                    payment_type_name,
                    month_name,
                    year,
                    month
                ORDER BY 
                    year,
                    month,
                    revenue_type,
                    revenue_type_record
            """

            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Process results to create a structured response
            response_data = {
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                },
                'summary': {
                    'total_revenue': sum(float(r['total_amount']) for r in results),
                    'total_records': len(results)
                },
                'breakdown_by_type': {},
                'details': results
            }


            # Create breakdown by revenue type
            for result in results:
                rev_type = result['revenue_type']
                if rev_type not in response_data['breakdown_by_type']:
                    response_data['breakdown_by_type'][rev_type] = {
                        'total': 0,
                        'records': []
                    }
                response_data['breakdown_by_type'][rev_type]['total'] += float(result['total_amount'])
                response_data['breakdown_by_type'][rev_type]['records'].append(result)

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)