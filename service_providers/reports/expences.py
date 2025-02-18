from django.db import connection
from django.http import JsonResponse
from django.views import View
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class ExpenseReportView(View):
    def get(self, request):
        try:
            # Get parameters from request
            church_id = request.GET.get('church_id')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            # Validate church_id
            if not church_id:
                return JsonResponse({'error': 'Church ID is required'}, status=400)

            # If dates not provided, use current month
            if not start_date or not end_date:
                today = date.today()
                start_date = date(today.year, today.month, 1)
                _, last_day = monthrange(today.year, today.month)
                end_date = date(today.year, today.month, last_day)
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # SQL query for expense details and totals
            query = """
                WITH monthly_expenses AS (
                    SELECT 
                        e.church_id,
                        e.amount,
                        e.date as transaction_date,
                        e.spent_by,
                        ec.category_name,
                        ec.budget as category_budget,
                        sp.church_name,
                        EXTRACT(MONTH FROM e.date) as month,
                        EXTRACT(YEAR FROM e.date) as year,
                        TO_CHAR(e.date, 'Month') as month_name
                    FROM service_providers_expense e
                    JOIN service_providers_expensecategory ec ON e.expense_category_id = ec.id
                    JOIN service_provider_table sp ON e.church_id = sp.id
                    WHERE e.church_id = %s
                    AND e.date BETWEEN %s AND %s
                )
                SELECT 
                    year,
                    month,
                    month_name,
                    category_name,
                    SUM(amount) as total_amount,
                    MAX(category_budget) as budget,
                    MAX(category_budget) - SUM(amount) as remaining_budget,
                    church_name,
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'transaction_date', transaction_date,
                            'amount', amount,
                            'spent_by', spent_by
                        ) ORDER BY transaction_date
                    ) as transactions
                FROM church_expense_view
                GROUP BY 
                    year, month, month_name, category_name, church_name
                ORDER BY 
                    year, month, category_name;
            """

            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(query, [church_id, start_date, end_date])
                columns = [col[0] for col in cursor.description]
                expenses = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Calculate totals
            total_expenses = sum(float(exp['total_amount']) for exp in expenses)
            total_budget = sum(float(exp['budget']) for exp in expenses)
            total_remaining = total_budget - total_expenses

            # Group by month for better organization
            monthly_summary = {}
            for expense in expenses:
                month_key = f"{int(expense['year'])}-{int(expense['month']):02d}"
                if month_key not in monthly_summary:
                    monthly_summary[month_key] = {
                        'year': int(expense['year']),
                        'month': int(expense['month']),
                        'month_name': expense['month_name'].strip(),
                        'church_name': expense['church_name'],
                        'categories': [],
                        'month_total': 0,
                        'month_budget': 0,
                        'month_remaining': 0
                    }

                monthly_summary[month_key]['categories'].append({
                    'category_name': expense['category_name'],
                    'total_amount': float(expense['total_amount']),
                    'budget': float(expense['budget']),
                    'remaining_budget': float(expense['remaining_budget']),
                    'transactions': expense['transactions']
                })

                monthly_summary[month_key]['month_total'] += float(expense['total_amount'])
                monthly_summary[month_key]['month_budget'] += float(expense['budget'])
                monthly_summary[month_key]['month_remaining'] += float(expense['remaining_budget'])

            response_data = {
                'summary': {
                    'total_expenses': total_expenses,
                    'total_budget': total_budget,
                    'total_remaining': total_remaining,
                    'period': {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d')
                    }
                },
                'monthly_data': list(monthly_summary.values())
            }

            return JsonResponse(response_data, safe=False)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)