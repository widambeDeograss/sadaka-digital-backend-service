from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ..models import Zaka, Sadaka, CardsNumber


class ZakaMonthlyTotalsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        church_id = request.query_params.get('church_id')
        current_year = timezone.now().year
        all_months = [datetime(current_year, m, 1) for m in range(1, 13)]  # List of all months in the current year
        final_result = []

        if not church_id:
            return Response({"detail": "church_id is required."}, status=400)

        # Fetch zaka records filtered by church_id and for the current year
        queryset = Zaka.objects.filter(church_id=church_id, date__year=current_year)

        # Group by card number and month, sum the zaka_amount, and include mhumini names
        aggregated_data = (
            queryset
            .values(
                'bahasha__card_no',  # Card number
                'bahasha__mhumini__first_name',  # Member's first name
                'bahasha__mhumini__last_name'  # Member's last name
            )
            .annotate(
                month=TruncMonth('date'),  # Extract the month from the date
                total_amount=Sum('zaka_amount')  # Sum the zaka amount per month
            )
            .values(
                'bahasha__card_no', 'bahasha__mhumini__first_name',
                'bahasha__mhumini__last_name', 'month', 'total_amount'
            )
            .order_by('bahasha__card_no', 'month')  # Order by card number and month
        )

        # Initialize card_data to store totals by card number and month
        card_data = {}

        for item in aggregated_data:
            card_no = item['bahasha__card_no']
            first_name = item['bahasha__mhumini__first_name']
            last_name = item['bahasha__mhumini__last_name']
            member_name = f"{first_name} {last_name}"
            month = item['month']
            total_amount = item['total_amount']

            # Initialize card data if not already present
            if card_no not in card_data:
                card_data[card_no] = {
                    'member_name': member_name,
                    'totals_by_month': {month.strftime('%Y-%m'): total_amount}
                }

            # Update the total_amount for the existing month
            card_data[card_no]['totals_by_month'][month.strftime('%Y-%m')] = total_amount

        # Fill missing months with zero for each card number
        for card_no, data in card_data.items():
            result = {
                'card_no': card_no,
                'member_name': data['member_name'],
                'months': []
            }
            for month in all_months:
                month_str = month.strftime('%Y-%m')
                total_amount = data['totals_by_month'].get(month_str, 0)  # Return 0 if no data for that month
                result['months'].append({
                    'month': month_str,
                    'total_amount': total_amount
                })
            final_result.append(result)

        return Response(final_result)


class SadakaWeeklyView(APIView):
    permission_classes = [AllowAny]

    def get_week_boundaries(self, year, month):
        """Divide the current month into four weekly periods."""
        first_day = datetime(year, month, 1)
        weeks = []
        for i in range(4):
            week_start = first_day + timedelta(days=i * 7)
            week_end = week_start + timedelta(days=6)
            if week_end.month != month:
                week_end = datetime(year, month + 1, 1) - timedelta(days=1)  # Ensure last week doesn't go over the month
            weeks.append((week_start, week_end))
        return weeks

    def get(self, request, *args, **kwargs):
        church_id = request.query_params.get('church_id')
        current_date = timezone.now()
        current_year = current_date.year
        current_month = current_date.month

        if not church_id:
            return Response({"detail": "church_id is required."}, status=400)

        # Get all card numbers (bahasha) associated with the church
        card_numbers = CardsNumber.objects.filter(mhumini__church_id=church_id)

        # Fetch sadaka records filtered by church_id and current month
        queryset = Sadaka.objects.filter(
            church_id=church_id,
            date__year=current_year,
            date__month=current_month
        )

        # Get four-week boundaries for the current month
        weeks = self.get_week_boundaries(current_year, current_month)

        # Prepare the result for each card number with sadaka amounts for each week
        data = []
        for card in card_numbers:
            card_data = {
                "card_no": card.card_no,
                "mhumini_first_name": card.mhumini.first_name,
                "mhumini_last_name": card.mhumini.last_name,
                "weekly_sadaka": []
            }

            # Loop through each week and calculate the total sadaka for this card
            for week_start, week_end in weeks:
                total_sadaka = queryset.filter(
                    bahasha_id=card.id,  # Match the current card number
                    date__gte=week_start,
                    date__lte=week_end
                ).aggregate(total_sadaka=Sum('sadaka_amount'))['total_sadaka'] or 0

                # Add the week's sadaka data
                card_data["weekly_sadaka"].append({
                    "week_start": week_start.date(),
                    "week_end": week_end.date(),
                    "total_sadaka": total_sadaka
                })

            # Add this card's data to the final result
            data.append(card_data)

        return Response(data)

