from io import BytesIO
import pandas as pd
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated,    IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .operations.message import pushMessage
from .serializer import *
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1000

class SystemPackageListCreateView(ListCreateAPIView):
    queryset = SystemPackage.objects.all()
    serializer_class = SystemPackageSerializer
    permission_classes = [IsAuthenticated]


class SystemPackageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SystemPackage.objects.all()
    serializer_class = SystemPackageSerializer
    permission_classes = [IsAuthenticated]


class SystemOfferListCreateView(ListCreateAPIView):
    queryset = SystemOffer.objects.all()
    serializer_class = SystemOfferSerializer
    permission_classes = [IsAuthenticated]


class SystemOfferRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SystemOffer.objects.all()
    serializer_class = SystemOfferSerializer
    permission_classes = [IsAuthenticated]


class ServiceProviderListCreateView(ListCreateAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]


class ServiceProviderByAdminView(RetrieveAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        sp_admin_id = self.kwargs.get('sp_admin_id')
        try:
            service_provider = ServiceProvider.objects.get(sp_admin=sp_admin_id)
        except ServiceProvider.DoesNotExist:
            raise Http404("Service Provider not found")

        # Get the active package for the service provider
        active_package = None
        try:
            active_package = Package.objects.get(church=service_provider, is_active=True)
        except Package.DoesNotExist:
            active_package = None  # No active package found

        # Return both the service provider and active package
        return {
            "service_provider": service_provider,
            "active_package": active_package,
        }

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        # Serialize the service provider data
        service_provider_data = self.get_serializer(obj['service_provider']).data

        # Prepare the response
        response_data = {
            "service_provider": service_provider_data,
            "active_package": obj['active_package'] if obj['active_package'] is None else PackageSerializer(
                obj['active_package']).data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ServiceProviderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]


class PackageListCreateView(ListCreateAPIView):
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get packages for a specific church_id, with filter if church_id is passed as a query parameter
        church_id = self.request.query_params.get('church_id')
        queryset = Package.objects.all()

        if church_id:
            queryset = queryset.filter(church_id=church_id)

        # Deactivate expired active packages
        current_time = timezone.now()  # Use timezone-aware datetime
        for package in queryset.filter(is_active=True):
            if package.package_end_date < current_time:
                package.is_active = False
                package.save()
                # TODO: Add logic here to notify the user the package has expired or about to expire
                print(f"TODO: Notify that package {package.id} has expired.")
            elif (package.package_end_date - current_time).days <= 7:  # Example threshold of 7 days
                # TODO: Notify user about package ending soon
                print(f"TODO: Notify that package {package.id} is about to expire.")

        return queryset

    # def create(self, request, *args, **kwargs):
    #     response = super().create(request, *args, **kwargs)
    #     church_id = request.data.get('church')
    #
    #     if church_id:
    #         # Get all packages for the same church that are still active
    #         active_packages = Package.objects.filter(church_id=church_id, is_active=True)
    #
    #         for package in active_packages:
    #             if package.package_end_date < datetime.now():
    #                 package.is_active = False
    #                 package.save()
    #                 # TODO: Notify user that the package has expired
    #                 print(f"TODO: Notify that package {package.id} has expired.")
    #             elif (package.package_end_date - datetime.now()).days <= 7:  # Threshold of 7 days
    #                 # TODO: Notify user about package ending soon
    #                 print(f"TODO: Notify that package {package.id} is about to expire.")
    #
    #     return response


class PackageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     # Get packages for a specific church_id, with filter if church_id is passed as a query parameter
    #     church_id = self.request.query_params.get('church_id')
    #     queryset = Package.objects.all()
    #
    #     if church_id:
    #         queryset = queryset.filter(church_id=church_id)
    #
    #     # Deactivate expired active packages
    #     for package in queryset.filter(is_active=True):
    #         if package.package_end_date < datetime.now():
    #             package.is_active = False
    #             package.save()
    #             # TODO: Add logic here to notify the user the package has expired or about to expire
    #             print(f"TODO: Notify that package {package.id} has expired.")
    #         elif (package.package_end_date - datetime.now()).days <= 7:  # Example threshold of 7 days
    #             # TODO: Notify user about package ending soon
    #             print(f"TODO: Notify that package {package.id} is about to expire.")
    #
    #     return queryset

class CreateSpManager(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        user_data = {
            "username": request.data.get("username"),
            "email":request.data.get('email'),
            "firstname": request.data.get("first_name"),
            "lastname": request.data.get("last_name"),
            "fullname": request.data.get("full_name"),
            "phone": request.data.get("phone"),
            "password": request.data.get("password"),
            "is_sp_manager":True,
            "role": request.data.get("role"),
        }

        manager_data = {
            "church": request.data.get("church"),
            "inserted_by": request.data.get("inserted_by"),
            "updated_by": request.data.get("updated_by"),
            "active": request.data.get("active", True),
        }
        print(user_data)
        try:
            user_serializer =  UserSerializer(data=user_data)
            print(user_serializer)
            if not  user_serializer.is_valid():
                return Response(
                    {"message": "User validation failed", "errors": user_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user =  user_serializer.save()

            print(user)

            manager_data["sp_manager"] = user.id
            manager_serializer =  SpManagerSerializer(data=manager_data)
            if not manager_serializer.is_valid():
                return Response(
                    {"message": "Manager validation failed", "errors": user_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            manager_serializer.save()
            return Response(
                {
                    "message": "User and Marketing Team Member created successfully",
                    "user": user_serializer.data,
                    "marketing_team": manager_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            transaction.set_rollback(True)
            return Response(
                {"message": "An error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SpManagerListView(viewsets.ModelViewSet):
    queryset = SpManagers.objects.filter(deleted=False)
    serializer_class = SpManagerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        user_id =  self.request.query_params.get('user')
        if church_id:
            return SpManagers.objects.filter(church=church_id)
        elif user_id:
            return  SpManagers.objects.filter(sp_manager=user_id)
        return SpManagers.objects.all()

class SpManagerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = SpManagers.objects.all()
    serializer_class = SpManagerSerializer
    permission_classes = [IsAuthenticated]


class KandaViewListCreate(ListCreateAPIView):
    queryset = Kanda.objects.all()
    serializer_class = KandaSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Kanda.objects.filter(church=church_id)
        return Kanda.objects.all()

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class KandaViewUpdateDistroy(RetrieveUpdateDestroyAPIView):
    queryset = Kanda.objects.all()
    serializer_class = KandaSerializer
    permission_classes = [IsAuthenticated]


class JumuiyaViewListCreate(ListCreateAPIView):
    queryset = Jumuiya.objects.all()
    serializer_class = JumuiyaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Jumuiya.objects.filter(church=church_id)
        return Jumuiya.objects.all()

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        # Get query parameters
        church_id = request.query_params.get('church_id')
        search_query = request.query_params.get('search', '').strip()

        # Start with base queryset
        queryset = self.get_queryset()

        # Apply search filter if search query exists
        if search_query:
            queryset = queryset.filter(
                Q(church=church_id) if church_id else Q(),
                Q(name__icontains=search_query) if search_query else Q()
            )

        # Perform ordering if specified
        ordering = request.query_params.get('ordering')
        if ordering:
            try:
                queryset = queryset.order_by(ordering)
            except Exception:
                # Fallback to default ordering if invalid
                pass

        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # If not paginated, return full results
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class JumuiyaViewUpdateDistrol(RetrieveUpdateDestroyAPIView):
    queryset = Jumuiya.objects.all()
    serializer_class = JumuiyaSerializer
    permission_classes = [IsAuthenticated]


class WahuminiPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class WahuminiListCreateView(ListCreateAPIView):
    serializer_class = WahuminiSerializer
    permission_classes = [IsAuthenticated]
    # pagination_class = WahuminiPagination

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        jumuiya_id =  self.request.query_params.get('jumuiya')
        queryset = Wahumini.objects.all()

        if church_id:
            queryset = queryset.filter(church=church_id)
        elif jumuiya_id:
            queryset = queryset.filter(jumuiya=jumuiya_id)

        # Optimize database queries
        queryset = queryset.select_related('church') \
            .defer('jumuiya')  # Defer large fields if any

        return queryset

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Fetch all data (bypass pagination)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
            return response

        # Default behavior (paginated response)
        return super().list(request, *args, **kwargs)

# class WahuminiListCreateView(ListCreateAPIView):
#     queryset = Wahumini.objects.all()
#     serializer_class = WahuminiSerializer
#     permission_classes = [IsAuthenticated]
#
#     @method_decorator(cache_page(60 * 15))
#     def get_queryset(self):
#         church_id = self.request.query_params.get('church_id')
#         if church_id:
#             return Wahumini.objects.filter(church=church_id)
#         return Wahumini.objects.all()


class WahuminiRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Wahumini.objects.all()
    serializer_class = WahuminiSerializer
    permission_classes = [IsAuthenticated]


class CardsNumberNumberPagination(PageNumberPagination):
    page_size = 600  # Adjust based on performance needs
    page_size_query_param = 'page_size'
    max_page_size = 500

class CardsNumberListCreateView(ListCreateAPIView):
    queryset = CardsNumber.objects.all()
    serializer_class = CardsNumberSerializer
    permission_classes = [IsAuthenticated]
    # pagination_class = CardsNumberNumberPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_fields = ['bahasha_type', 'card_status']

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return CardsNumber.objects.filter(church=church_id)
        return CardsNumber.objects.all()

    # @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Fetch all data (bypass pagination)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
            return response
        return super().list(request, *args, **kwargs)



class CardsNumberRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = CardsNumber.objects.all()
    serializer_class = CardsNumberSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        print("------------------------")
        """
        Retrieve a single CardsNumber object by card_no and optionally church_id.
        """
        card_no = self.kwargs.get("card_no")
        church_id = self.request.query_params.get("church_id")

        if not card_no:
            raise ValueError("Card number must be provided.")

        # Filter criteria
        filter_criteria = {"card_no": card_no}
        if church_id:
            filter_criteria["mhumini__church_id"] = church_id

        # Retrieve object with caching and optimized query
        return get_object_or_404(CardsNumber.objects.select_related('mhumini'), **filter_criteria)


class PaymentTypeListCreateView(ListCreateAPIView):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return PaymentType.objects.filter(church=church_id)
        return PaymentType.objects.all()

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



class PaymentTypeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    permission_classes = [IsAuthenticated]


class SadakaTypeListCreateView(ListCreateAPIView):
    queryset = SadakaTypes.objects.all()
    serializer_class = SadakaTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')

        if church_id:
            queryset = SadakaTypes.objects.filter(church_id=church_id)

            return queryset
        else:
             return SadakaTypes.objects.none()


class SadakaTypeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SadakaTypes.objects.all()
    serializer_class = SadakaTypeSerializer
    permission_classes = [IsAuthenticated]



class SadakaListCreateView(ListCreateAPIView):
    queryset = Sadaka.objects.all()
    serializer_class = SadakaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        filter_type = self.request.query_params.get('filter')
        year = self.request.query_params.get('year', timezone.now().year)
        queryset = Sadaka.objects.all()

        if church_id:
            queryset = queryset.filter(church_id=church_id)

        if year:
            queryset = queryset.filter(inserted_at__year=year)

        if filter_type == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(inserted_at__date=today)
        else:
            queryset = queryset.order_by('-inserted_at')

        return queryset


    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Use the filtered queryset from get_queryset
            queryset = self.get_queryset()
            serializer = SadakaExportSerializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=sadaka_export.xlsx'
            return response

        # If not exporting, use the standard list behavior
        return super().list(request, *args, **kwargs)


class SadakaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Sadaka.objects.all()
    serializer_class = SadakaSerializer
    permission_classes = [IsAuthenticated]


class ZakaListCreateView(ListCreateAPIView):
    queryset = Zaka.objects.all()
    serializer_class = ZakaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        zaka = serializer.save()
        if zaka.bahasha:
            # Retrieve the mhumini's details for the SMS
            mhumini = zaka.bahasha.mhumini
            amount_paid = zaka.zaka_amount
            month = zaka.date.strftime("%B")  # Get the month name
            year = zaka.date.year

            # Compose the SMS message in Swahili
            message = (f"Tumsifu Yesu Kristu,\n Mpendwa {mhumini.first_name} {mhumini.last_name}, tumepokea zaka yako ya Tsh {amount_paid} kwa mwezi wa {month} {year}. \n"
                       f"imepokelewa kwa {zaka.payment_type.name}, namba ya bahasha {zaka.bahasha.card_no}"
                       f" Asante kwa mchango wako, Mungu akubariki.\n KAMATI YA ZAKA, PAROKIA YA BMC MAKABE. ")
            print(message)
            # Send the SMS using your existing SMS method
            pushMessage(message, mhumini.phone_number)


        else:
            pass
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        filter_type = self.request.query_params.get('filter')
        year = self.request.query_params.get('year',
                                             timezone.now().year)
        if church_id:
            queryset = Zaka.objects.filter(church_id=church_id)

            queryset = queryset.filter(inserted_at__year=year)

            if filter_type == 'today':
                today = timezone.now().date()
                queryset = queryset.filter(inserted_at__date=today)
            else:
                queryset = queryset.order_by('-inserted_at')

            return queryset
        else:
            return Zaka.objects.none()

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Use the filtered queryset from get_queryset
            queryset = self.get_queryset()
            serializer = ZakaExportSerializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=zaka_export.xlsx'
            return response

        # If not exporting, use the standard list behavior
        return super().list(request, *args, **kwargs)


class ZakaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Zaka.objects.all()
    serializer_class = ZakaSerializer
    permission_classes = [IsAuthenticated]


class PaymentTypeTransferListCreateView(ListCreateAPIView):
    queryset = PaymentTypeTransfer.objects.all()
    serializer_class = PaymentTypeTransferSerializer
    permission_classes = [IsAuthenticated]


class PaymentTypeTransferRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = PaymentTypeTransfer.objects.all()
    serializer_class = PaymentTypeTransferSerializer
    permission_classes = [IsAuthenticated]


class RevenueListCreateView(ListCreateAPIView):
    queryset = Revenue.objects.all()
    serializer_class = RevenueSerializer
    permission_classes = [IsAuthenticated]


class RevenueUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        revenue_type_record = request.data.get("revenue_type_record")
        revenue_type = request.data.get("revenue_type")

        try:
            # Find the Revenue object by `revenue_type_record` and `revenue_type`
            revenue = Revenue.objects.get(
                revenue_type_record=revenue_type_record,
                revenue_type=revenue_type
            )
        except Revenue.DoesNotExist:
            return Response(
                {"error": "Revenue record not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update the record with the new data
        serializer = RevenueSerializer(revenue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RevenueRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Revenue.objects.all()
    serializer_class = RevenueSerializer
    permission_classes = [IsAuthenticated]


class ExpenseListCreateView(ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        filter_type = self.request.query_params.get('filter')
        year = self.request.query_params.get('year',
                                             timezone.now().year)
        if church_id:
            queryset = Expense.objects.filter(church_id=church_id)

            queryset = queryset.filter(inserted_at__year=year)

            if filter_type == 'today':
                today = timezone.now().date()
                queryset = queryset.filter(inserted_at__date=today)
            else:
                queryset = queryset.order_by('-inserted_at')

            return queryset
        else:
            return Expense.objects.none()


class ExpenseRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]


class ExpenseCategoryListCreateView(ListCreateAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]


class ExpenseCategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]


class MchangoListCreateView(ListCreateAPIView):
    queryset = Mchango.objects.all()
    serializer_class = MchangoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Mchango.objects.filter(church=church_id)
        return Mchango.objects.all()
    

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MchangoSerializer(queryset, many=True)
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Fetch all data (bypass pagination)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
            return response
        return Response(serializer.data)


class MchangoRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Mchango.objects.all()
    serializer_class = MchangoSerializer
    permission_classes = [IsAuthenticated]


class MchangoPaymentListCreateView(ListCreateAPIView):
    queryset = MchangoPayments.objects.all()
    serializer_class = MchangoPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        mchango_id = self.request.query_params.get('mchango_id')

        filter_type = self.request.query_params.get('filter')

        if mchango_id:
            queryset = MchangoPayments.objects.filter(mchango_id=mchango_id)

            if filter_type == 'today':
                today = timezone.now().date()
                queryset = queryset.filter(inserted_at__date=today)
            else:
                queryset = queryset.order_by('-inserted_at')

            return queryset
        else:
            return MchangoPayments.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MchangoPaymentSerializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Overrides the default perform_create to update the related Mchango's collected_amount.
        """
        # Save the MchangoPayment instance
        mchango_payment = serializer.save()

        try:
            # Lock the Mchango instance to prevent race conditions
            mchango = Mchango.objects.select_for_update().get(id=mchango_payment.mchango_id)
        except Mchango.DoesNotExist:
            # If the Mchango does not exist, rollback the transaction
            raise serializers.ValidationError("Mchango does not exist.")

        # Update the collected_amount
        mchango.collected_amount += mchango_payment.amount
        mchango.save()

class MchangoPaymentRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = MchangoPayments.objects.all()
    serializer_class = MchangoSerializer
    permission_classes = [IsAuthenticated]

class AhadiListCreateView(ListCreateAPIView):
    queryset = Ahadi.objects.all()
    serializer_class = AhadiSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        mchango_id = self.request.query_params.get('mchango_id')
        wahumini_id = self.request.query_params.get('mhumini')
        filter_type = self.request.query_params.get('filter')
        year = self.request.query_params.get('year', timezone.now().year)

        if church_id:
            queryset = Ahadi.objects.filter(church_id=church_id, created_at__year=year)

            if mchango_id:
                queryset = queryset.filter(mchango=mchango_id)
            if wahumini_id:
                queryset = queryset.filter(wahumini=wahumini_id)
            if filter_type == 'today':
                today = timezone.now().date()
                queryset = queryset.filter(created_at__date=today)
            else:
                queryset = queryset.order_by('-created_at')

            return queryset

        return Ahadi.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = AhadiSerializer(queryset, many=True)
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Fetch all data (bypass pagination)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
            return response
        return Response(serializer.data)
    

class AhadiRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Ahadi.objects.all()
    serializer_class = AhadiSerializer
    permission_classes = [IsAuthenticated]


class AhadiPaymentListCreateView(ListCreateAPIView):
    queryset = AhadiPayments.objects.all()
    serializer_class = AhadiPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ahadi_id = self.request.query_params.get('ahadi_id')

        queryset = Ahadi.objects.filter(ahadi=ahadi_id)

        queryset = queryset.order_by('-created_at')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MchangoPaymentSerializer(queryset, many=True)
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Fetch all data (bypass pagination)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
            return response
        return Response(serializer.data)


    @transaction.atomic
    def perform_create(self, serializer):

        # Save the Ahadi payment instance
        ahadi_payment = serializer.save()


        try:

            # Lock the Mchango instance to prevent race conditions
            ahadi = Ahadi.objects.select_for_update().get(id=ahadi_payment.ahadi.id)

        except Ahadi.DoesNotExist:
            # If the Mchango does not exist, rollback the transaction
            raise serializers.ValidationError("Ahadi does not exist.")

        # Update the collected_amount
        ahadi.paid_amount += ahadi_payment.amount
        ahadi.save()

        if ahadi.mchango:
          mchango_payment =   MchangoPayments.objects.create(
                mchango=ahadi.mchango,
                amount=ahadi_payment.amount,
                payment_type=ahadi_payment.payment_type,
                mhumini=ahadi_payment.mhumini,
                inserted_by=ahadi_payment.inserted_by,
                updated_by=ahadi_payment.updated_by,
            )
          mchango =  Mchango.objects.get(id=ahadi.mchango.id)
          mchango.collected_amount += ahadi_payment.amount
          mchango.save()
          Revenue.objects.create(
              amount=ahadi_payment.amount,
              church=ahadi.church,
              payment_type=ahadi_payment.payment_type,
              revenue_type="Michango",
              revenue_type_record=mchango_payment.id,
              date_received=ahadi_payment.inserted_at.date(),
              created_by=ahadi_payment.inserted_by,
              updated_by=ahadi_payment.updated_by,
          )
        else:
            # If no Mchango, create a Sadaka record
           sadaka = Sadaka.objects.create(
                church=ahadi.church,
                sadaka_amount=ahadi_payment.amount,
                collected_by=ahadi_payment.inserted_by,  # Assuming inserted_by is the collector
                payment_type=ahadi_payment.payment_type,
                date=ahadi_payment.inserted_at.date(),  # Use the payment date
                inserted_by=ahadi_payment.inserted_by,
                updated_by=ahadi_payment.updated_by,
            )
           Revenue.objects.create(
                amount=ahadi_payment.amount,
                church=ahadi.church,
                payment_type=ahadi_payment.payment_type,
                revenue_type="Sadaka",
                revenue_type_record=sadaka.id,
                date_received=ahadi_payment.inserted_at.date(),
                created_by=ahadi_payment.inserted_by,
                updated_by=ahadi_payment.updated_by,
            )
        return ahadi_payment



class MavunoListCreateView(ListCreateAPIView):
    queryset = Mavuno.objects.all().order_by('-inserted_at')
    serializer_class = MavunoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Mavuno.objects.filter(church=church_id)
        return Mavuno.objects.all()
    
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MavunoSerializer(queryset, many=True)
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Fetch all data (bypass pagination)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
            return response
        return Response(serializer.data)

class MavunoRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Mavuno.objects.all()
    serializer_class = MavunoSerializer
    permission_classes = [IsAuthenticated]


class MavunoPaymentListCreateView(ListCreateAPIView):
    queryset = MavunoPayments.objects.all()
    serializer_class = MavunoPaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        mavuno_id = self.request.query_params.get('mavuno_id')
        if mavuno_id:
            return MavunoPayments.objects.filter(mavuno_id=mavuno_id)
        return MavunoPayments.objects.all()


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MavunoPaymentSerializer(queryset, many=True)
        export = request.query_params.get('export', None)

        if export == 'excel':
            # Fetch all data (bypass pagination)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Prepare the response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
            return response
        return Response(serializer.data)

    @transaction.atomic
    def perform_create(self, serializer):
        mavuno_payment = serializer.save()

        try:
            mavuno = Mavuno.objects.select_for_update().get(id=mavuno_payment.mavuno_id)

        except Mavuno.DoesNotExist:
            raise serializers.ValidationError("Mavuno does not exist.")

        mavuno.collected_amount += mavuno_payment.amount
        print(mavuno.jumuiya.namba_ya_simu)
        pushMessage(
            f"Tumsifu Yesu Kristu,\n Mavuno ya Mpendwa {mavuno_payment.mhumini.first_name + ' ' + mavuno_payment.mhumini.last_name} kiasi cha Tsh {mavuno_payment.amount} \n"
            f"Yamepokelewa kwa {mavuno_payment.payment_type.name}, Jumuiya {mavuno.jumuiya.name}. Jumla ya mavuno {mavuno.collected_amount} \n Mungu akubariki.",

            mavuno.jumuiya.address
        )
        pushMessage(
            f"Tumsifu Yesu Kristu,\n Mavuno ya Mpendwa {mavuno_payment.mhumini.first_name + ' ' + mavuno_payment.mhumini.last_name} kiasi cha Tsh {mavuno_payment.amount} \n"
                    f"Yamepokelewa kwa {mavuno_payment.payment_type.name}, Jumuiya {mavuno.jumuiya.name}. Jumla ya mavuno {mavuno.collected_amount}. \nMungu akubariki.",
                    mavuno.jumuiya.namba_ya_simu,
        )

        mavuno.save()


class MavunoPaymentRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = MavunoPayments.objects.all()
    serializer_class = MavunoPaymentSerializer
    permission_classes = [IsAuthenticated]