from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, F, Window
from django.db.models.functions import TruncMonth
from django.utils import timezone
from decimal import Decimal
from service_providers.models import Revenue, Expense, MchangoPayments, MavunoPayments


class MonthlyFinancialReportGenerator:
    def __init__(self, church, year=None):
        self.church = church
        self.year = year or timezone.now().year
        self.months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

    def monthly_revenue_report(self):
        """
        Generate monthly revenue report by type and record
        """
        revenue_report = Revenue.objects.filter(
            church=self.church,
            date_received__year=self.year
        ).annotate(
            month=TruncMonth('date_received')
        ).values('month', 'revenue_type', 'revenue_type_record').annotate(
            total_amount=Sum('amount')
        ).order_by('month')

        # Initialize report with zero values for all months
        report = {month: {} for month in self.months}

        for entry in revenue_report:
            month = entry['month'].strftime('%B')
            revenue_type = entry['revenue_type']
            record_type = entry['revenue_type_record']
            amount = float(entry['total_amount'])

            if revenue_type not in report[month]:
                report[month][revenue_type] = {}
            report[month][revenue_type][record_type] = amount

        return report

    def monthly_expense_report(self):
        """
        Generate monthly expense report by category
        """
        expense_report = Expense.objects.filter(
            church=self.church,
            date__year=self.year
        ).annotate(
            month=TruncMonth('date')
        ).values('month', 'expense_category__category_name').annotate(
            total_amount=Sum('amount')
        ).order_by('month')

        # Initialize report with zero values for all months
        report = {month: {} for month in self.months}

        for entry in expense_report:
            month = entry['month'].strftime('%B')
            category = entry['expense_category__category_name']
            amount = float(entry['total_amount'])
            report[month][category] = amount

        return report

    def monthly_mchango_report(self):
        """
        Generate monthly Mchango (Contribution) report
        """
        mchango_report = MchangoPayments.objects.filter(
            mchango__church=self.church,
            inserted_at__year=self.year
        ).annotate(
            month=TruncMonth('inserted_at')
        ).values('month', 'mchango__mchango_name').annotate(
            total_amount=Sum('amount')
        ).order_by('month')

        # Initialize report with zero values for all months
        report = {month: {} for month in self.months}

        for entry in mchango_report:
            month = entry['month'].strftime('%B')
            mchango_name = entry['mchango__mchango_name']
            amount = float(entry['total_amount'])
            report[month][mchango_name] = amount

        return report

    def monthly_mavuno_report(self):
        """
        Generate monthly Mavuno report by Jumuiya
        """
        mavuno_report = MavunoPayments.objects.filter(
            mavuno__church=self.church,
            inserted_at__year=self.year
        ).annotate(
            month=TruncMonth('inserted_at')
        ).values('month', 'mavuno__jumuiya__name', 'mavuno__name').annotate(
            total_amount=Sum('amount')
        ).order_by('month')

        # Initialize report with zero values for all months
        report = {month: {} for month in self.months}

        for entry in mavuno_report:
            month = entry['month'].strftime('%B')
            jumuiya_name = entry['mavuno__jumuiya__name']
            mavuno_name = entry['mavuno__name']
            amount = float(entry['total_amount'])

            if jumuiya_name not in report[month]:
                report[month][jumuiya_name] = {}
            report[month][jumuiya_name][mavuno_name] = amount

        return report


class MonthlyReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['GET'])
    def monthly_revenue(self, request):
        """
        Monthly revenue report endpoint
        """
        church = request.query_params.get('church')
        year = request.query_params.get('year', timezone.now().year)

        report_generator = MonthlyFinancialReportGenerator(church, year)
        report = report_generator.monthly_revenue_report()

        return Response(report)

    @action(detail=False, methods=['GET'])
    def monthly_expenses(self, request):
        """
        Monthly expenses report endpoint
        """
        church = request.query_params.get('church')
        year = request.query_params.get('year', timezone.now().year)

        report_generator = MonthlyFinancialReportGenerator(church, year)
        report = report_generator.monthly_expense_report()

        return Response(report)

    @action(detail=False, methods=['GET'])
    def monthly_mchango(self, request):
        """
        Monthly Mchango report endpoint
        """
        church = request.query_params.get('church')
        year = request.query_params.get('year', timezone.now().year)

        report_generator = MonthlyFinancialReportGenerator(church, year)
        report = report_generator.monthly_mchango_report()

        return Response(report)

    @action(detail=False, methods=['GET'])
    def monthly_mavuno(self, request):
        """
        Monthly Mavuno report endpoint
        """
        church = request.query_params.get('church')
        year = request.query_params.get('year', timezone.now().year)

        report_generator = MonthlyFinancialReportGenerator(church, year)
        report = report_generator.monthly_mavuno_report()

        return Response(report)