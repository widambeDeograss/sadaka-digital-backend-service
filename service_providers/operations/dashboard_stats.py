from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count

from service_providers.models import Wahumini, CardsNumber, Revenue, Jumuiya


class ChurchDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        church_id = request.query_params.get('church_id')
        current_year = datetime.now().year

        if not church_id:
            return Response({"error": "Church ID is required."}, status=400)

        try:
            # Total Wahumini
            total_wahumini = Wahumini.objects.filter(church_id=church_id).count()

            # Total Card Numbers
            total_card_numbers = CardsNumber.objects.filter(mhumini__church_id=church_id).count()

            # Total Revenue
            total_revenue = Revenue.objects.filter(church_id=church_id,  date_received__year=current_year).aggregate(
                total=Sum('amount')
            )['total'] or 0

            # Total Jumuiya
            total_jumuiya = Jumuiya.objects.filter(church_id=church_id).count()

            data = {
                "total_wahumini": total_wahumini,
                "total_card_numbers": total_card_numbers,
                "total_revenue": total_revenue,
                "total_jumuiya": total_jumuiya,
            }
            return Response(data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
