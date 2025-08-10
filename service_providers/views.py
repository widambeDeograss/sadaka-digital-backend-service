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
from .serializer import *
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .sms_queue_service import SMSQueueService
import logging

logger = logging.getLogger(__name__)


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

        logging.info(f"Creating SP Manager with data: {manager_data}")

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

            logging.info(f"SP Manager created successfully: {manager_serializer.data}") 
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
            logging.error(f"Error creating SP Manager: {str(e)}")
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
        logger.info(f"Fetching Jumuiya for church_id: {church_id}")
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
    pagination_class = WahuminiPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'first_name',
        'last_name',
        'phone_number',
        'email',
        'jumuiya__name',
        'jumuiya__kanda__name',
    ]
    ordering_fields = ['created_at', 'updated_at', 'first_name', 'last_name']
    ordering = ['-created_at']

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
    page_size = 600
    page_size_query_param = 'page_size'
    max_page_size = 500

class CardsNumberListCreateView(ListCreateAPIView):
    queryset = CardsNumber.objects.all()
    serializer_class = CardsNumberSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CardsNumberNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['mhumini__first_name', 'mhumini__last_name',
                     'card_no', 'mhumini__jumuiya__name', 'mhumini__jumuiya__kanda__name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

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
        logger.info(f"Fetching CardsNumber for card_no: {card_no}, church_id: {church_id}")

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

        logger.info(f"Fetching Sadaka for church_id: {church_id}, filter_type: {filter_type}, year: {year}")

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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['bahasha__mhumini__first_name', 'bahasha__mhumini__last_name', 
                     'bahasha__card_no', 'bahasha__mhumini__jumuiya__name']
    ordering_fields = ['date', 'zaka_amount', 'inserted_at']
    ordering = ['-inserted_at']
    sms_service = SMSQueueService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        logger.info(f"Creating Zaka entry with data: {validated_data}")

        # Pre-check 1: Monthly entry validation
        bahasha = validated_data.get('bahasha')
        date = validated_data.get('date')
        if bahasha and date:
            month = date.month
            year = date.year
            # Check for existing entry in same month/year
            if Zaka.objects.filter(
                    bahasha=bahasha,
                    date__month=month,
                    date__year=year
            ).exists():
                logger.warning(f"Zaka entry for bahasha {bahasha} already exists in {month}/{year}.")
                return Response(
                    {"detail": "Zaka entry for this bahasha already exists in this month."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create record if validation passes
        zaka = serializer.save()
        response_data = serializer.data
        logger.info(f"Zaka entry created successfully: {response_data}")
        headers = self.get_success_headers(serializer.data)

        # Pre-check 2: Phone number notification
        if zaka.bahasha:
            mhumini = zaka.bahasha.mhumini
            if not mhumini.phone_number:
                logger.warning(f"Zaka recorded successfully, but SMS not sent: Mhumini missing phone number.")
                # Add warning to response
                response_data = dict(response_data)
                response_data['warning'] = "Zaka recorded successfully, but SMS not sent: Mhumini missing phone number."
            else:
                # Send SMS if phone exists
                amount_paid = zaka.zaka_amount
                month = zaka.date.strftime("%B")
                year = zaka.date.year
                message = (
                    f"Kristu,\nMpendwa {mhumini.first_name} {mhumini.last_name}, "
                    f"tumepokea zaka yako ya Tsh {amount_paid} kwa mwezi {month} {year}. "
                    f"Mungu akubariki.\nMawasiliano: 0677050573\nPAROKIA YA BMC MAKABE."
                )
                self.sms_service.add_to_queue(message, mhumini.phone_number, mhumini.first_name + " " + mhumini.last_name)

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = Zaka.objects.all()
        
        # Church filter
        church_id = self.request.query_params.get('church_id')
        if church_id:
            queryset = queryset.filter(church_id=church_id)
        else:
            return Zaka.objects.none()
        
        # Date filters
        filter_type = self.request.query_params.get('filter')
        year = self.request.query_params.get('year', timezone.now().year)
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')

        logger.info(f"Fetching Zaka for church_id: {church_id}, filter_type: {filter_type}, year: {year}, from_date: {from_date}, to_date: {to_date}")
        
        # Filter by year if no specific date range is provided
        if not (from_date or to_date):
            queryset = queryset.filter(inserted_at__year=year)
        
        # Apply date range filters if provided
        if from_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                queryset = queryset.filter(inserted_at__date__gte=from_date)
            except ValueError:
                pass
                
        if to_date:
            try:
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                queryset = queryset.filter(inserted_at__date__lte=to_date)
            except ValueError:
                pass
        
        # Quick filters
        if filter_type == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(inserted_at__date=today)
        
        # Search by mhumini name, card_no, jumuiya
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(bahasha__mhumini__first_name__icontains=search_query) |
                Q(bahasha__mhumini__last_name__icontains=search_query) |
                Q(bahasha__card_no__icontains=search_query) |
                Q(bahasha__mhumini__jumuiya__name__icontains=search_query)
            )
            
        return queryset.order_by('-inserted_at')

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
        queryset = self.filter_queryset(self.get_queryset())

        if export:
            serializer = ZakaExportSerializer(queryset, many=True)
            data = serializer.data
            
            # Convert the data to a DataFrame
            df = pd.DataFrame(data)
            
            if export == 'excel':
                # Create an Excel file in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Zaka Records')
                
                # Prepare the response
                output.seek(0)
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=zaka_export.xlsx'
                return response
                
            elif export == 'pdf':
                # Create a PDF file
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=zaka_export.pdf'

                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=landscape(letter),
                    leftMargin=20,
                    rightMargin=20,
                    topMargin=20,
                    bottomMargin=20
                )
                elements = []
                
                # Add title
                styles = getSampleStyleSheet()
                elements.append(Paragraph("Zaka Records Report", styles['Title']))
                elements.append(Spacer(1, 12))
                max_col_count = len(df.columns)
                page_width = landscape(letter)[0] - doc.leftMargin - doc.rightMargin
                col_width = page_width / max_col_count
                col_widths = [col_width] * max_col_count
                
                # Create table data
                table_data = [df.columns.tolist()]  # Header row
                for _, row in df.iterrows():
                    table_data.append(row.tolist())
                
                # Create the table
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elements.append(table)
                doc.build(elements)
                
                pdf = buffer.getvalue()
                buffer.close()
                response.write(pdf)
                return response
        
        # If not exporting, use standard list behavior with pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ZakaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Zaka.objects.all()
    serializer_class = ZakaSerializer
    permission_classes = [IsAuthenticated]
    sms_service = SMSQueueService()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Store the old amount before update
        old_amount = instance.zaka_amount
        old_date = instance.date

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        logger.info(f"Updating Zaka entry {instance.id} with data: {validated_data}")

        self.perform_update(serializer)
        updated_instance = serializer.instance

        # Only send SMS if the amount has changed
        if updated_instance.zaka_amount != old_amount or updated_instance.date != old_date:
            if updated_instance.bahasha:
                mhumini = updated_instance.bahasha.mhumini
                if not mhumini.phone_number:
                    logger.warning(
                        f"Zaka updated successfully, but SMS not sent: Mhumini missing phone number."
                    )
                else:
                    amount_paid = updated_instance.zaka_amount
                    month = updated_instance.date.strftime("%B")
                    year = updated_instance.date.year
                    message = (
                        f"Kristu,\nMpendwa {mhumini.first_name} {mhumini.last_name}, "
                        f"zaka yako kwa mwezi {month} {year} imebadilishwa kuwa Tsh {amount_paid}. "
                        f"Mungu akubariki.\nMawasiliano: 0677050573\nPAROKIA YA BMC MAKABE."
                    )
                    self.sms_service.add_to_queue(
                        message,
                        mhumini.phone_number,
                        f"{mhumini.first_name} {mhumini.last_name}"
                    )
                    logger.info(f"Correction SMS queued for {mhumini.phone_number}")

        return Response(serializer.data)


class PaymentTypeTransferListCreateView(ListCreateAPIView):
    serializer_class = PaymentTypeTransferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['from_payment_type', 'to_payment_type']

    def get_queryset(self):
        queryset = PaymentTypeTransfer.objects.all()

        # Get query parameters
        from_payment_type = self.request.query_params.get('from_payment_type')
        to_payment_type = self.request.query_params.get('to_payment_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        church_id = self.request.query_params.get('church')

        logger.info(f"Fetching PaymentTypeTransfer with filters: from_payment_type={from_payment_type}, to_payment_type={to_payment_type}, start_date={start_date}, end_date={end_date}, church_id={church_id}")

        # Filter by church (service provider)
        if church_id:
            queryset = queryset.filter(church_id=church_id)

        # Filter by from_payment_type if provided
        if from_payment_type:
            queryset = queryset.filter(from_payment_type_id=from_payment_type)

        # Filter by to_payment_type if provided
        if to_payment_type:
            queryset = queryset.filter(to_payment_type_id=to_payment_type)

        # Date range filtering
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(
                    transfer_date__gte=start_date,
                    transfer_date__lte=end_date
                )
            except ValueError:
                pass  # Handle invalid date format if needed

        return queryset.select_related('from_payment_type', 'to_payment_type', 'church')


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

        logger.info(f"Updating Revenue for revenue_type_record: {revenue_type_record}, revenue_type: {revenue_type}")

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

        logger.info(f"Created MchangoPayment: {mchango_payment.id}")

        try:
            # Lock the Mchango instance to prevent race conditions
            mchango = Mchango.objects.select_for_update().get(id=mchango_payment.mchango_id)
            logger.info(f"Locked Mchango instance: {mchango.id}")
        except Mchango.DoesNotExist:
            # If the Mchango does not exist, rollback the transaction
            raise serializers.ValidationError("Mchango does not exist.")
        logger.info(f"Updating Mchango instance: {mchango.id}")
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
        logger.info(f"Created AhadiPayment: {ahadi_payment.id}")


        try:

            # Lock the Mchango instance to prevent race conditions
            ahadi = Ahadi.objects.select_for_update().get(id=ahadi_payment.ahadi.id)

        except Ahadi.DoesNotExist:
            # If the Mchango does not exist, rollback the transaction
            raise serializers.ValidationError("Ahadi does not exist.")
        logger.info(f"Updating Ahadi instance: {ahadi.id}")
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
          logger.info(f"Created MchangoPayment based on AHADI: {mchango_payment.id}")
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
          logger.info(f"Updated Mchango instance: {mchango.id}")
        else:
            # If no Mchango, create a Sadaka record
           logger.info(f"Creating Sadaka for church: {ahadi.church.id}, amount: {ahadi_payment.amount}")
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
           logger.info(f"Created Sadaka: {sadaka.id}")
        return ahadi_payment



class MavunoListCreateView(ListCreateAPIView):
    queryset = Mavuno.objects.all().order_by('-inserted_at')
    serializer_class = MavunoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        mavuno_type = self.request.query_params.get('mavuno_type')
        if church_id and mavuno_type:
            return Mavuno.objects.filter(church=church_id, mavuno_type=mavuno_type)
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
    sms_service = SMSQueueService()

    def get_queryset(self):
        mavuno_id = self.request.query_params.get('mavuno_id')
        logger.info(f"Fetching MavunoPayments for mavuno_id: {mavuno_id}")
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
        logger.info(f"Created MavunoPayment: {mavuno_payment.id}")

        try:
            mavuno = Mavuno.objects.select_for_update().get(id=mavuno_payment.mavuno_id)

            logger.info(f"Locked Mavuno instance: {mavuno.id}")

        except Mavuno.DoesNotExist:
            raise serializers.ValidationError("Mavuno does not exist.")

        mavuno.collected_amount += mavuno_payment.amount
        logger.info(f"Updated Mavuno instance: {mavuno.id}")
        message = f"Tumsifu Yesu Kristu,\n Mavuno ya Mpendwa {mavuno_payment.mhumini.first_name + ' ' + mavuno_payment.mhumini.last_name} kiasi cha Tsh {mavuno_payment.amount} \n" \
                  f"Yamepokelewa kwa {mavuno_payment.payment_type.name}, Jumuiya {mavuno.jumuiya.name}. Jumla ya mavuno {mavuno.collected_amount} \n Mungu awabariki. Mawasiliano: 0677050573 PAROKIA YA BMC MAKABE."

     
        self.sms_service.add_to_queue(message, mavuno.jumuiya.namba_ya_simu, mavuno.jumuiya.name)
      
        self.sms_service.add_to_queue(message, mavuno.jumuiya.address, mavuno.jumuiya.name)
        logger.info(f"SMS notification queued for MavunoPayment: {mavuno_payment.id}")

        mavuno.save()


class MavunoPaymentRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = MavunoPayments.objects.all()
    serializer_class = MavunoPaymentSerializer
    permission_classes = [IsAuthenticated]