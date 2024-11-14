from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import TruncMonth, Coalesce, ExtractMonth
from django.utils import timezone
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta
from rest_framework.views import APIView
from django.db import models
from service_providers.models import MchangoPayments, Mchango, Ahadi


class MchangoStats(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        church_id = request.query_params.get("church_id")
        current_year = datetime.now().year
        data_type = request.query_params.get("type")

        # Check query type and return the appropriate response
        if data_type == "mchango_stats":
            return self.get_mchango_stats(church_id, current_year)
        elif data_type == "mchango_totals":
            return self.get_mchango_totals(church_id)
        else:
            return Response({"error": "Invalid query type"}, status=400)

    def get_mchango_stats(self, church_id, current_year):
        # Retrieve monthly total payments for each mchango in the current year
        mchangos = Mchango.objects.filter(church_id=church_id)
        mchango_stats = []

        for mchango in mchangos:
            # Query monthly totals for each mchango payment within the current year
            monthly_totals = (
                MchangoPayments.objects.filter(
                    mchango=mchango,
                    inserted_at__year=current_year
                )
                .annotate(month=TruncMonth("inserted_at"))
                .values("month")
                .annotate(total=Sum("amount"))
                .order_by("month")
            )

            # Prepare data for 12 months, defaulting to zero if no data exists for a month
            monthly_data = [0] * 12  # Initialize with zero for each month
            for entry in monthly_totals:
                month_index = entry["month"].month - 1  # Zero-based month index
                monthly_data[month_index] = entry["total"]

            mchango_stats.append({
                "mchango_name": mchango.mchango_name,
                "monthly_data": monthly_data,
            })

        # Structuring data for the area chart
        area_chart_data = {
            "series": [
                {
                    "name": mchango_stat["mchango_name"],
                    "data": mchango_stat["monthly_data"],
                    "offsetY": 0,
                }
                for mchango_stat in mchango_stats
            ]
        }

        return Response({
            "area_chart_data": area_chart_data,
        })

    from django.db.models import DecimalField, Sum, Value
    from django.db.models.functions import Coalesce

    def get_mchango_totals(self, church_id):
        # Current date and monthly period range
        current_date = timezone.now()
        current_month_start = current_date.replace(day=1)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)

        # Retrieve all mchango instances for the specified church
        mchangos = Mchango.objects.filter(church_id=church_id)
        mchango_data = []

        for mchango in mchangos:
            # Calculate the total collected amount for each mchango from MchangoPayments
            total_collected = MchangoPayments.objects.filter(mchango=mchango).aggregate(
                collected=Coalesce(Sum('amount', output_field=DecimalField()), Value(0, output_field=DecimalField()))
            )['collected']

            # Calculate the total collected for the current and previous month
            current_month_collected = MchangoPayments.objects.filter(
                mchango=mchango,
                # inserted_at__gte=current_month_start
            ).aggregate(
                collected=Coalesce(Sum('amount', output_field=DecimalField()), Value(0, output_field=DecimalField()))
            )['collected']

            previous_month_collected = MchangoPayments.objects.filter(
                mchango=mchango,
                inserted_at__gte=previous_month_start,
                inserted_at__lte=previous_month_end
            ).aggregate(
                collected=Coalesce(Sum('amount', output_field=DecimalField()), Value(0, output_field=DecimalField()))
            )['collected']

            # Calculate the monthly percentage change
            if previous_month_collected > 0:
                monthly_change = ((current_month_collected - previous_month_collected) / previous_month_collected) * 100
            else:
                monthly_change = 0  # No previous data

            # Calculate the percentage of the collected amount to the target
            target_amount = mchango.target_amount
            percentage_collected = (total_collected / target_amount * 100) if target_amount > 0 else 0

            # Calculate the new target with a 5% increase applied
            # new_target_amount = target_amount * 1.05  # 5% increase from the original target

            # Add the data for this mchango to the list
            mchango_data.append({
                "mchango_name": mchango.mchango_name,
                "target_amount": target_amount,
                # "new_target_amount": round(new_target_amount, 2),
                "collected_amount": total_collected,
                "percentage_collected": round(percentage_collected, 2),
                "current_month_collected": current_month_collected,
                "previous_month_collected": previous_month_collected,
                "monthly_change": round(monthly_change, 2),
                "status": mchango.status,
                "date": mchango.date,
            })

        return Response(mchango_data)


class MchangoStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, mchango_id, *args, **kwargs):
        # Ensure the Mchango exists
        try:
            mchango = Mchango.objects.get(id=mchango_id)
        except Mchango.DoesNotExist:
            return Response({"detail": "Mchango not found."}, status=404)

        # Process and return stats (e.g., collected amount, remaining amount)
        stats = self.get_mchango_stats(mchango)

        return Response(stats)

    def get_mchango_stats(self, mchango):
        # Collect the stats based on mchango's payments and other data
        total_collected = mchango.mchangopayments_set.aggregate(total_collected=models.Sum('amount'))[
                              'total_collected'] or 0
        remaining_amount = mchango.target_amount - total_collected
        # total_ahadi = mchango.ahadi_set.aggregate(total_ahadi=models.Sum('ahadi'))['total_ahadi'] or 0

        # Assuming you want to calculate collected amount by month in the current year
        monthly_collections = self.get_monthly_collections(mchango)

        return {
            "mchango_name": mchango.mchango_name,
            "collected_amount": total_collected,
            "remaining_amount": remaining_amount,
            # "total_ahadi": total_ahadi,
            "monthly_collections": monthly_collections,
        }

    def get_monthly_collections(self, mchango):
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth
        current_year = datetime.now().year
        # Get payments aggregated by month for the current year
        # payments = mchango.mchangopayments_set.filter(
        #     inserted_at__year=current_year
        # ).annotate(month=TruncMonth('inserted_at')).values('month').annotate(total=Sum('amount')).order_by('month')
        #
        # return [{"month": payment['month'].strftime('%B'), "total_collected": payment['total']} for payment in payments]
        payments = mchango.mchangopayments_set.filter(
            inserted_at__year=current_year
        ).annotate(month=TruncMonth('inserted_at')).values('month').annotate(total=Sum('amount')).order_by('month')

        return [{"month": payment['month'].strftime('%B'), "total_collected": payment['total']} for payment in payments]
