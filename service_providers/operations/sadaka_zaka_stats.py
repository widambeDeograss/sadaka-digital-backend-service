from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

from .message import pushMessage
from ..models import Zaka, Sadaka, CardsNumber


class SadakaZakaStats(APIView):
    permission_classes = [IsAuthenticated]

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
            inserted_at__date=today
        ).aggregate(total_cash=Sum('sadaka_amount'))['total_cash'] or 0

        sadaka_other_total = Sadaka.objects.filter(
            church_id=church_id,
            inserted_at__date=today
        ).exclude(
            payment_type__name='Cash'
        ).aggregate(total_other=Sum('sadaka_amount'))['total_other'] or 0

        sadaka_total_today = Sadaka.objects.filter(
            church_id=church_id,
            inserted_at__date=today
        ).aggregate(total_today=Sum('sadaka_amount'))['total_today'] or 0

        sadaka_total_year = Sadaka.objects.filter(
            church_id=church_id,
            inserted_at__year=current_year
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
           inserted_at__year = current_year,
           inserted_at__month = today.month
        ).aggregate(total_cash=Sum('zaka_amount'))['total_cash'] or 0

        zaka_other_total = Zaka.objects.filter(
            church_id=church_id,
            inserted_at__year=current_year,
            inserted_at__month=today.month
        ).exclude(
            payment_type__name='Cash'
        ).aggregate(total_other=Sum('zaka_amount'))['total_other'] or 0

        zaka_total_today = Zaka.objects.filter(
            church_id=church_id,
            inserted_at__year=current_year,
            inserted_at__month=today.month
        ).aggregate(total_today=Sum('zaka_amount'))['total_today'] or 0

        zaka_total_year = Zaka.objects.filter(
            church_id=church_id,
            inserted_at__year=current_year
        ).aggregate(total_year=Sum('zaka_amount'))['total_year'] or 0

        return Response({
            "total_cash": zaka_cash_total,
            "total_other": zaka_other_total,
            "total_today": zaka_total_today,
            "total_year": zaka_total_year,
        })

    def get_area_chart_data(self, church_id, current_year):
        sadaka_monthly = (
            Sadaka.objects.filter(church_id=church_id, inserted_at__year=current_year)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('sadaka_amount'))
            .order_by('month')
        )

        zaka_monthly = (
            Zaka.objects.filter(church_id=church_id, inserted_at__year=current_year)
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



class CheckZakaPresenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        end_month = request.query_params.get('end_month')
        end_year = request.query_params.get('end_year')
        church_id = request.query_params.get('church_id')
        query_type = request.query_params.get('query_type')  # Determines the action: 'check' or 'reminder'

        if not month or not year:
            return Response({"error": "Month and year are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12:
                return Response({"error": "Invalid month. Must be between 1 and 12."}, status=status.HTTP_400_BAD_REQUEST)
            if query_type == "range" and (not end_month or not end_year):
                return Response({"error": "Both end_month and end_year are required for range queries."},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Month and year must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        if query_type == "check":
            # Check presence
            card_details = self.get_zaka_card_details_for_month_year(month, year, church_id)
            return Response({"card_details": card_details}, status=status.HTTP_200_OK)
        elif query_type == "reminder":
            # Send reminders
            reminder_status = self.send_unpaid_zaka_reminders(month, year, church_id)
            return Response(reminder_status, status=status.HTTP_200_OK)
        elif query_type == "range":
            # Check presence range
            card_details = self.get_zaka_card_details_for_range(month, year, end_month, end_year, church_id)
            return Response({"card_details": card_details}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid query_type. Use 'check', 'reminder', or 'range'."},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_zaka_card_details_for_month_year(self, month, year, church_id):
        zaka_cards = CardsNumber.objects.filter(bahasha_type='zaka', church=church_id).select_related('mhumini')
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        card_details = []

        for card in zaka_cards:
            has_entry = Zaka.objects.filter(
                bahasha=card,
                church=church_id,
                date__gte=start_date,
                date__lt=end_date
            ).exists()

            card_details.append({
                "card_no": card.card_no,
                "mhumini_name": card.mhumini.first_name,
                "jumuiya":card.mhumini.jumuiya.name,
                "kanda": card.mhumini.jumuiya.kanda.name,
                "present": has_entry
            })

        return card_details

    def get_zaka_card_details_for_range(self, start_month, start_year, end_month, end_year, church_id):
        zaka_cards = CardsNumber.objects.filter(bahasha_type='zaka', mhumini__church=church_id).select_related(
            'mhumini')
        month = int(start_month)
        year = int(start_year)
        end_month = int(end_month)
        end_year = int(end_year)
        # Generate the date ranges
        start_date = datetime(year, month, 1)
        end_date = datetime(end_year, end_month + 1, 1) if end_month < 12 else datetime(end_year + 1, 1, 1)

        card_details = []

        for card in zaka_cards:
            entries = Zaka.objects.filter(
                bahasha=card,
                church=church_id,
                date__gte=start_date,
                date__lt=end_date
            )

            monthly_presence = {}
            for single_month in range(start_month, end_month + 1):
                month_start_date = datetime(start_year, single_month, 1)
                month_end_date = datetime(start_year, single_month + 1, 1) if single_month < 12 else datetime(
                    start_year + 1, 1, 1)
                has_entry = Zaka.objects.filter(
                    bahasha=card,
                    church=church_id,
                    date__gte=month_start_date,
                    date__lt=month_end_date
                ).exists()
                monthly_presence[single_month] = has_entry

            card_details.append({
                "card_no": card.card_no,
                "mhumini_name": card.mhumini.first_name,
                "jumuiya": card.mhumini.jumuiya.name,
                "kanda": card.mhumini.jumuiya.kanda.name,
                "monthly_presence": monthly_presence
            })

        return card_details

    def send_unpaid_zaka_reminders(self, month, year, church_id):
        zaka_cards = CardsNumber.objects.filter(bahasha_type='zaka', church=church_id).select_related('mhumini')
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        unpaid_wahumini = []

        for card in zaka_cards:
            has_entry = Zaka.objects.filter(
                bahasha=card,
                church=church_id,
                date__gte=start_date,
                date__lt=end_date
            ).exists()

            if not has_entry:
                unpaid_wahumini.append(card.mhumini)

        # Send SMS to each unpaid wahumini
        for mhumini in unpaid_wahumini:
            print(mhumini.phone_number)
            message = f"Habari {mhumini.first_name} {mhumini.first_name} , huu ni ujumbe wa kukukumbusha kutoa zaka yako kwa mwezi wa {month} mwaka {year}. Asante kwa mchango wako na Mungu akubariki."
            pushMessage(message, mhumini.phone_number)  # Assuming `phone_number` field exists

        return {"status": "SMS reminders sent to unpaid wahumini"}
