from django.db import transaction
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializer import *


class SystemPackageListCreateView(ListCreateAPIView):
    queryset = SystemPackage.objects.all()
    serializer_class = SystemPackageSerializer
    permission_classes = [AllowAny]


class SystemPackageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SystemPackage.objects.all()
    serializer_class = SystemPackageSerializer
    permission_classes = [AllowAny]


class SystemOfferListCreateView(ListCreateAPIView):
    queryset = SystemOffer.objects.all()
    serializer_class = SystemOfferSerializer
    permission_classes = [AllowAny]


class SystemOfferRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SystemOffer.objects.all()
    serializer_class = SystemOfferSerializer
    permission_classes = [AllowAny]


class ServiceProviderListCreateView(ListCreateAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]


class ServiceProviderByAdminView(RetrieveAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]


class PackageListCreateView(ListCreateAPIView):
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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

class SpManagerListView(viewsets.ModelViewSet):
    queryset = SpManagers.objects.filter(deleted=False)
    serializer_class = SpManagerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return SpManagers.objects.filter(church=church_id)
        return SpManagers.objects.all()

class SpManagerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = SpManagers.objects.all()
    serializer_class = SpManagerSerializer
    permission_classes = [AllowAny]


class KandaViewListCreate(ListCreateAPIView):
    queryset = Kanda.objects.all()
    serializer_class = KandaSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Kanda.objects.filter(church=church_id)
        return Kanda.objects.all()

class KandaViewUpdateDistroy(RetrieveUpdateDestroyAPIView):
    queryset = Kanda.objects.all()
    serializer_class = KandaSerializer
    permission_classes = [AllowAny]

class JumuiyaViewListCreate(ListCreateAPIView):
    queryset = Jumuiya.objects.all()
    serializer_class = JumuiyaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Jumuiya.objects.filter(church=church_id)
        return Jumuiya.objects.all()

class JumuiyaViewUpdateDistrol(RetrieveUpdateDestroyAPIView):
    queryset = Jumuiya.objects.all()
    serializer_class = JumuiyaSerializer
    permission_classes = [AllowAny]

class WahuminiListCreateView(ListCreateAPIView):
    queryset = Wahumini.objects.all()
    serializer_class = WahuminiSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Wahumini.objects.filter(church=church_id)
        return Wahumini.objects.all()


class WahuminiRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Wahumini.objects.all()
    serializer_class = WahuminiSerializer
    permission_classes = [AllowAny]


class CardsNumberListCreateView(ListCreateAPIView):
    queryset = CardsNumber.objects.all()
    serializer_class = CardsNumberSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return CardsNumber.objects.filter(mhumini__church_id=church_id)
        return CardsNumber.objects.all()

    
class CardsNumberRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = CardsNumber.objects.all()
    serializer_class = CardsNumberSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        card_no = self.kwargs.get("card_no")
        return get_object_or_404(CardsNumber, card_no=card_no)


class PaymentTypeListCreateView(ListCreateAPIView):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return PaymentType.objects.filter(church=church_id)
        return PaymentType.objects.all()


class PaymentTypeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    permission_classes = [AllowAny]


class SadakaListCreateView(ListCreateAPIView):
    queryset = Sadaka.objects.all()
    serializer_class = SadakaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        filter_type = self.request.query_params.get('filter')
        year = self.request.query_params.get('year',
                                             timezone.now().year)
        if church_id:
            queryset = Sadaka.objects.filter(church_id=church_id)

            queryset = queryset.filter(inserted_at__year=year)

            if filter_type == 'today':
                today = timezone.now().date()
                queryset = queryset.filter(inserted_at__date=today)
            else:
                queryset = queryset.order_by('-inserted_at')

            return queryset
        else:
            return Sadaka.objects.none()


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = SadakaSerializer(queryset, many=True)
        return Response(serializer.data)


class SadakaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Sadaka.objects.all()
    serializer_class = SadakaSerializer
    permission_classes = [AllowAny]


class ZakaListCreateView(ListCreateAPIView):
    queryset = Zaka.objects.all()
    serializer_class = ZakaSerializer
    permission_classes = [AllowAny]

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


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ZakaSerializer(queryset, many=True)
        return Response(serializer.data)


class ZakaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Zaka.objects.all()
    serializer_class = ZakaSerializer
    permission_classes = [AllowAny]


class PaymentTypeTransferListCreateView(ListCreateAPIView):
    queryset = PaymentTypeTransfer.objects.all()
    serializer_class = PaymentTypeTransferSerializer
    permission_classes = [AllowAny]


class PaymentTypeTransferRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = PaymentTypeTransfer.objects.all()
    serializer_class = PaymentTypeTransferSerializer
    permission_classes = [AllowAny]


class RevenueListCreateView(ListCreateAPIView):
    queryset = Revenue.objects.all()
    serializer_class = RevenueSerializer
    permission_classes = [AllowAny]


class RevenueUpdateView(APIView):
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]


class ExpenseListCreateView(ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]


class ExpenseCategoryListCreateView(ListCreateAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [AllowAny]


class ExpenseCategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [AllowAny]


class MchangoListCreateView(ListCreateAPIView):
    queryset = Mchango.objects.all()
    serializer_class = MchangoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        if church_id:
            return Mchango.objects.filter(church=church_id)
        return Mchango.objects.all()


class MchangoRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Mchango.objects.all()
    serializer_class = MchangoSerializer
    permission_classes = [AllowAny]


class MchangoPaymentListCreateView(ListCreateAPIView):
    queryset = MchangoPayments.objects.all()
    serializer_class = MchangoPaymentSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

class AhadiListCreateView(ListCreateAPIView):
    queryset = Ahadi.objects.all()
    serializer_class = AhadiSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        church_id = self.request.query_params.get('church_id')
        mchango_id = self.request.query_params.get('mchango_id')
        filter_type = self.request.query_params.get('filter')
        year = self.request.query_params.get('year', timezone.now().year)

        if church_id:
            queryset = Ahadi.objects.filter(church_id=church_id, created_at__year=year)

            if mchango_id:
                queryset = queryset.filter(mchango=mchango_id)

            if filter_type == 'today':
                today = timezone.now().date()
                queryset = queryset.filter(created_at__date=today)
            else:
                queryset = queryset.order_by('-created_at')

            return queryset

        return Ahadi.objects.none()

class AhadiRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Ahadi.objects.all()
    serializer_class = AhadiSerializer
    permission_classes = [AllowAny]


class AhadiPaymentListCreateView(ListCreateAPIView):
    queryset = AhadiPayments.objects.all()
    serializer_class = AhadiPaymentSerializer
    permission_classes = [AllowAny]

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

        return ahadi_payment

