from django.db.models import Sum, Count, Q, F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from service_providers.models import Ahadi, Mchango


class AhadiStats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        church_id = request.query_params.get("church_id")

        # Total amount of all Ahadi without specific Mchango
        ahadi_without_mchango = Ahadi.objects.filter(church_id=church_id, mchango__isnull=True)
        total_amount_without_mchango = ahadi_without_mchango.aggregate(total=Sum('amount'))['total'] or 0
        total_paid_without_mchango = ahadi_without_mchango.aggregate(total_paid=Sum('paid_amount'))['total_paid'] or 0
        total_pending_without_mchango = total_amount_without_mchango - total_paid_without_mchango

        # Total pending Ahadi amounts, total paid Ahadi amounts, and counts
        ahadi_queryset = Ahadi.objects.filter(church_id=church_id)

        # Total Ahadi pending amounts (amount - paid_amount for all records)
        total_pending_amount = ahadi_queryset.aggregate(
            total_pending=Sum(F('amount') - F('paid_amount'))
        )['total_pending'] or 0

        # Total Ahadi paid amounts
        total_paid_amount = ahadi_queryset.aggregate(total_paid=Sum('paid_amount'))['total_paid'] or 0

        # Count of pending Ahadi (where paid_amount < amount)
        total_pending_ahadi_count = ahadi_queryset.filter(paid_amount__lt=F('amount')).count()

        # Count of fully paid Ahadi (where paid_amount >= amount)
        total_fully_paid_ahadi_count = ahadi_queryset.filter(paid_amount__gte=F('amount')).count()

        # Calculate totals for each Mchango
        mchango_totals = []
        for mchango in Mchango.objects.filter(church_id=church_id):
            ahadi_for_mchango = Ahadi.objects.filter(church_id=church_id, mchango=mchango)

            mchango_total_amount = ahadi_for_mchango.aggregate(total=Sum('amount'))['total'] or 0
            mchango_total_paid = ahadi_for_mchango.aggregate(total_paid=Sum('paid_amount'))['total_paid'] or 0
            mchango_total_pending = mchango_total_amount - mchango_total_paid

            mchango_totals.append({
                "mchango_name": mchango.mchango_name,
                "total_amount": mchango_total_amount,
                "total_paid": mchango_total_paid,
                "total_pending": mchango_total_pending,
            })

        # Response data
        return Response({
            "total_pending_amount": total_pending_amount,
            "total_paid_amount": total_paid_amount,
            "total_pending_ahadi_count": total_pending_ahadi_count,
            "total_fully_paid_ahadi_count": total_fully_paid_ahadi_count,
            "total_amount_without_mchango": total_amount_without_mchango,
            "total_paid_without_mchango": total_paid_without_mchango,
            "total_pending_without_mchango": total_pending_without_mchango,
            "mchango_totals": mchango_totals,
        })
