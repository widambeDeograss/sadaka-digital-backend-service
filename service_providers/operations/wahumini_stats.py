from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from ..models import Wahumini, Zaka, Sadaka, Mchango, Ahadi, MchangoPayments


class WahuminiStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wahumini_id = request.query_params.get('mhumini')
        current_year = date.today().year

        # Fetch totals for Zaka contributions
        zaka_total = Zaka.objects.filter(
            bahasha__mhumini_id=wahumini_id,
            date__year=current_year
        ).aggregate(total=Sum('zaka_amount'))['total'] or 0

        # Fetch totals for Sadaka contributions
        sadaka_total = Sadaka.objects.filter(
            bahasha__mhumini_id=wahumini_id,
            date__year=current_year
        ).aggregate(total=Sum('sadaka_amount'))['total'] or 0

        # Fetch totals for Michango contributions
        michango_total = MchangoPayments.objects.filter(
            mhumini=wahumini_id,
            inserted_at__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Fetch totals for Ahadi contributions
        ahadi_total = Ahadi.objects.filter(
            wahumini=wahumini_id,
            created_at__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Monthly data for the area chart
        zaka_monthly = Zaka.objects.filter(
            bahasha__mhumini_id=wahumini_id,
            date__year=current_year
        ).values('date__month').annotate(monthly_total=Sum('zaka_amount')).order_by('date__month')

        sadaka_monthly = Sadaka.objects.filter(
            bahasha__mhumini_id=wahumini_id,
            date__year=current_year
        ).values('date__month').annotate(monthly_total=Sum('sadaka_amount')).order_by('date__month')

        return Response({
            'totals': {
                'zaka': zaka_total,
                'sadaka': sadaka_total,
                'michango': michango_total,
                'ahadi': ahadi_total
            },
            'monthly': {
                'zaka': zaka_monthly,
                'sadaka': sadaka_monthly
            }
        })
