from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ..models import Zaka, Sadaka, CardsNumber


class ZakaMonthlyTotalsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        church_id = request.query_params.get('church_id')
        year = request.query_params.get('year', timezone.now().year)

        try:
            year = int(year)
        except ValueError:
            return Response({"detail": "Year must be a valid integer."}, status=400)

        all_months = [datetime(year, m, 1) for m in range(1, 12)]
        final_result = []

        if not church_id:
            return Response({"detail": "church_id is required."}, status=400)

        queryset = Zaka.objects.filter(church_id=church_id, date__year=year)

        aggregated_data = (
            queryset
            .values(
                'bahasha__card_no',
                'bahasha__mhumini__first_name',
                'bahasha__mhumini__last_name' ,
                'bahasha__mhumini__jumuiya__name'
            )
            .annotate(
                month=TruncMonth('date'),
                total_amount=Sum('zaka_amount')
            )
            .values(
                'bahasha__card_no', 'bahasha__mhumini__first_name',
                'bahasha__mhumini__last_name','bahasha__mhumini__jumuiya__name',
                'bahasha__mhumini__jumuiya__kanda__name','month', 'total_amount'
            )
            .order_by('bahasha__card_no', 'month')
        )

        card_data = {}

        for item in aggregated_data:
            card_no = item['bahasha__card_no']
            first_name = item['bahasha__mhumini__first_name']
            last_name = item['bahasha__mhumini__last_name']
            member_name = f"{first_name} {last_name}"
            jumuiya_name = item['bahasha__mhumini__jumuiya__name']
            kanda_name = item['bahasha__mhumini__jumuiya__kanda__name']
            month = item['month']
            total_amount = item['total_amount']

            # Initialize card data if not already present
            if card_no not in card_data:
                card_data[card_no] = {
                    'member_name': member_name,
                    'jumuiya_name':jumuiya_name,
                    'kanda_name': kanda_name,
                    'totals_by_month': {month.strftime('%Y-%m'): total_amount}
                }

            # Update the total_amount for the existing month
            card_data[card_no]['totals_by_month'][month.strftime('%Y-%m')] = total_amount

        # Fill missing months with zero for each card number
        for card_no, data in card_data.items():
            result = {
                'card_no': card_no,
                'member_name': data['member_name'],
                'jumuiya_name':data['jumuiya_name'],
                'kanda_name':data['kanda_name'],
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
    permission_classes = [IsAuthenticated]

    def get_week_boundaries(self, year, month):
        """Divide the month into four weekly periods."""
        first_day = datetime(year, month, 1)
        last_day = (datetime(year, month + 1, 1) - timedelta(days=1)) if month < 12 else datetime(year, 12, 31)
        weeks = []

        current_start = first_day
        while current_start <= last_day:
            current_end = current_start + timedelta(days=6)
            if current_end > last_day:
                current_end = last_day  # End date of the last week in the month
            weeks.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)

        return weeks

    def get(self, request, *args, **kwargs):
        church_id = request.query_params.get('church_id')
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        # Default to the current year and month if not provided
        current_date = timezone.now()
        year = int(year) if year else current_date.year
        month = int(month) if month else current_date.month

        if not church_id:
            return Response({"detail": "church_id is required."}, status=400)

        # Get all card numbers (bahasha) associated with the church
        card_numbers = CardsNumber.objects.filter(mhumini__church_id=church_id, bahasha_type="sadaka")

        # Fetch sadaka records filtered by church_id, year, and month
        queryset = Sadaka.objects.filter(
            church_id=church_id,
            date__year=year,
            date__month=month
        )

        # Get weekly boundaries for the specified month and year
        weeks = self.get_week_boundaries(year, month)

        # Prepare the result for each card number with sadaka amounts for each week
        data = []
        for card in card_numbers:
            card_data = {
                "card_no": card.card_no,
                "mhumini_first_name": card.mhumini.first_name,
                "mhumini_last_name": card.mhumini.last_name,
                "weekly_sadaka": []
            }

            # Calculate total sadaka for each week
            for week_start, week_end in weeks:
                total_sadaka = queryset.filter(
                    bahasha=card.id,
                    date__gte=week_start,
                    date__lte=week_end
                ).aggregate(total_sadaka=Sum('sadaka_amount'))['total_sadaka'] or 0

                # Append weekly sadaka data
                card_data["weekly_sadaka"].append({
                    "week_start": week_start.date(),
                    "week_end": week_end.date(),
                    "total_sadaka": total_sadaka
                })

            # Add each card's data to the final result
            data.append(card_data)

        return Response(data)