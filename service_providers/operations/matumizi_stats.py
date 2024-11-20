from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from service_providers.models import Expense, ExpenseCategory


class ExpenseStats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        church_id = request.query_params.get("church_id")
        current_year = timezone.now().year

        # Filter expenses for the current year and the specified church
        expenses_this_year = Expense.objects.filter(
            church_id=church_id,
            date__year=current_year
        )

        # Aggregate total spending for each expense category
        category_totals = (
            expenses_this_year
            .values("expense_category__category_name")
            .annotate(total_spent=Sum("amount"))
            .order_by("expense_category__category_name")
        )

        # Calculate total spent across all categories
        total_spent = expenses_this_year.aggregate(total=Sum("amount"))["total"] or 0

        # Structure the response data
        result = {
            "total_spent": total_spent,
            "category_totals": [
                {
                    "category_name": entry["expense_category__category_name"],
                    "total_spent": entry["total_spent"]
                }
                for entry in category_totals
            ]
        }

        return Response(result)
