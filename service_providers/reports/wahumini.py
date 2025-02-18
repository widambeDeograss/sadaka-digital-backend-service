from django.db import connection
from django.http import JsonResponse
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.views import View


class MuhuminiContributionsView(View):
    def get(self, request):
        muhumini_id = request.GET.get('muhumini_id')
        jumuiya_id = request.GET.get('jumuiya_id')
        church_id = request.GET.get('church_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Set default date range to current month if not provided
        if not (start_date and end_date):
            today = date.today()
            start_date = today.replace(day=1)
            end_date = (today + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)

        where_clauses = []
        params = []

        if muhumini_id:
            where_clauses.append("mhumini_id = %s")
            params.append(muhumini_id)

        if jumuiya_id:
            where_clauses.append("jumuiya_name = (SELECT name FROM jumuiya WHERE id = %s)")
            params.append(jumuiya_id)

        if church_id:
            where_clauses.append("church_id = %s")
            params.append(church_id)

        where_clauses.append("transaction_date BETWEEN %s AND %s")
        params.extend([start_date, end_date])


        where_clause = " AND ".join(where_clauses)
        print(where_clause)

        query = f"""
            WITH monthly_totals AS (
                SELECT 
                    mhumini_id,
                    first_name,
                    last_name,
                    jumuiya_name,
                    kanda_name,
                    contribution_type,
                    contribution_detail,
                    year,
                    month_name,
                    SUM(amount) as total_amount,
                    COUNT(*) as contribution_count
                FROM muhumini_contributions_view
                WHERE {where_clause}
                GROUP BY 
                    mhumini_id, first_name, last_name, jumuiya_name, 
                    kanda_name, contribution_type, contribution_detail,
                    year, month_name
            )
            SELECT 
                mhumini_id,
                first_name,
                last_name,
                jumuiya_name,
                kanda_name,
                json_agg(json_build_object(
                    'contribution_type', contribution_type,
                    'contribution_detail', contribution_detail,
                    'year', year,
                    'month', month_name,
                    'total_amount', total_amount,
                    'contribution_count', contribution_count
                )) as contributions,
                SUM(total_amount) as grand_total
            FROM monthly_totals
            GROUP BY 
                mhumini_id, first_name, last_name, 
                jumuiya_name, kanda_name
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print(results)

        return JsonResponse({
            'data': results,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        })