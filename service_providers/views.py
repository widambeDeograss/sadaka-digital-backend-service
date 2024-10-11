from django.db import transaction
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, AllowAny
from rest_framework.response import Response
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
            return ServiceProvider.objects.get(sp_admin=sp_admin_id)
        except ServiceProvider.DoesNotExist:
            raise Http404("Service Provider not found")


class ServiceProviderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]



class PackageListCreateView(ListCreateAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]


class PackageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
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

        if church_id:
            queryset = Sadaka.objects.filter(church_id=church_id)

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

        if church_id:
            queryset = Zaka.objects.filter(church_id=church_id)

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


class RevenueRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Revenue.objects.all()
    serializer_class = RevenueSerializer
    permission_classes = [AllowAny]


class ExpenseListCreateView(ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]


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


class AhadiRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Ahadi.objects.all()
    serializer_class = AhadiSerializer
    permission_classes = [AllowAny]



