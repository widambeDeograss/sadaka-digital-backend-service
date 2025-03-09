from django.db import transaction
from rest_framework import serializers

from user_management.models import User
from user_management.serializer import UserSerializer
from .models import *


class SystemPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPackage
        fields = "__all__"


class SystemOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemOffer
        fields = "__all__"


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = "__all__"


class SpManagerSerializer(serializers.ModelSerializer):
    # sp_manager = UserSerializer()
    sp_manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sp_manager_details = UserSerializer(source='sp_manager', read_only=True)
    church = serializers.PrimaryKeyRelatedField(queryset=ServiceProvider.objects.all())
    church_details = ServiceProviderSerializer(source='church', read_only=True)

    class Meta:
        model = SpManagers
        fields = "__all__"


class PackageSerializer(serializers.ModelSerializer):
    package = serializers.PrimaryKeyRelatedField(queryset=SystemPackage.objects.all())
    package_details = SystemPackageSerializer(source='package',read_only=True)
    church = serializers.PrimaryKeyRelatedField(
        queryset=ServiceProvider.objects.all(),
        required=True
    )
    church_details = ServiceProviderSerializer(source='church', read_only=True)
    class Meta:
        model = Package
        fields = "__all__"

class KandaSerializer(serializers.ModelSerializer):
    church = serializers.PrimaryKeyRelatedField(
        queryset=ServiceProvider.objects.all(),
        required=True
    )
    church_details = ServiceProviderSerializer(source='church', read_only=True)

    class Meta:
        model = Kanda
        fields = '__all__'

class JumuiyaSerializer(serializers.ModelSerializer):
    kanda = serializers.PrimaryKeyRelatedField(
        queryset=Kanda.objects.all(),
        required=True
    )
    kanda_details = KandaSerializer(source='kanda', read_only=True)
    church = serializers.PrimaryKeyRelatedField(
        queryset=ServiceProvider.objects.all(),
        required=True
    )
    church_details = ServiceProviderSerializer(source='church', read_only=True)

    class Meta:
        model = Jumuiya
        fields = '__all__'


class WahuminiSerializer(serializers.ModelSerializer):
    jumuiya = serializers.PrimaryKeyRelatedField(
        queryset=Jumuiya.objects.all(),
        required=True
    )
    jumuiya_details = KandaSerializer(source='jumuiya', read_only=True)
    class Meta:
        model = Wahumini
        fields = "__all__"


class CardsNumberSerializer(serializers.ModelSerializer):
    mhumini = serializers.PrimaryKeyRelatedField(queryset=Wahumini.objects.all())
    mhumini_details = WahuminiSerializer(source='mhumini', read_only=True)
    class Meta:
        model = CardsNumber
        fields = "__all__"
        # depth = 2


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = "__all__"


class SadakaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SadakaTypes
        fields = "__all__"


class SadakaSerializer(serializers.ModelSerializer):
    bahasha = serializers.PrimaryKeyRelatedField(queryset=CardsNumber.objects.all(), required=False, allow_null=True)
    bahasha_details = CardsNumberSerializer(source='bahasha', read_only=True)
    sadaka_type = serializers.PrimaryKeyRelatedField(queryset=SadakaTypes.objects.all(), required=False, allow_null=True)
    type_details = SadakaTypeSerializer(source='sadaka_type', read_only=True)
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentType.objects.all(), required=False, allow_null=True)
    payment_type_details = PaymentTypeSerializer(source='payment_type', read_only=True)
    class Meta:
        model = Sadaka
        fields = "__all__"
        # depth=2

class SadakaExportSerializer(serializers.ModelSerializer):
    bahasha_card_number = serializers.SerializerMethodField()
    muumini = serializers.SerializerMethodField()
    sadaka_type_name = serializers.SerializerMethodField()
    sadaka_type_description = serializers.SerializerMethodField()
    payment_type_name = serializers.SerializerMethodField()
    jumuiya_details = serializers.SerializerMethodField()

    class Meta:
        model = Sadaka
        fields = [
            'id', 'sadaka_amount', 'inserted_at', 'inserted_by',
            'bahasha_card_number',
            'sadaka_type_name', 'sadaka_type_description',
            'payment_type_name', 'date',
        ]

    def get_bahasha_card_number(self, obj):
        if obj.bahasha:
            return obj.bahasha.card_no
        return None

    def get_muumini(self, obj):
        if obj.bahasha:
            return obj.bahasha.mhumini.first_name + " " + obj.bahasha.mhumini.last_name
        return None

    def get_sadaka_type_name(self, obj):
        if obj.sadaka_type:
            return obj.sadaka_type.name
        return None

    def get_sadaka_type_description(self, obj):
        if obj.sadaka_type:
            return obj.sadaka_type.description
        return None

    def get_payment_type_name(self, obj):
        if obj.payment_type:
            return obj.payment_type.name
        return None

    def get_payment_type_code(self, obj):
        if obj.payment_type:
            return obj.payment_type.description
        return None


class ZakaSerializer(serializers.ModelSerializer):
    bahasha = serializers.PrimaryKeyRelatedField(queryset=CardsNumber.objects.all(), required=False, allow_null=True)
    bahasha_details = CardsNumberSerializer(source='bahasha', read_only=True)
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentType.objects.all(), required=False, allow_null=True)
    payment_type_details = PaymentTypeSerializer(source='payment_type', read_only=True)
    class Meta:
        model = Zaka
        fields = "__all__"


class ZakaExportSerializer(serializers.ModelSerializer):
    bahasha_card_number = serializers.SerializerMethodField()
    muumini = serializers.SerializerMethodField()
    payment_type_name = serializers.SerializerMethodField()
    jumuiya_details = serializers.SerializerMethodField()

    class Meta:
        model = Zaka
        fields = [
            'id',
            'zaka_amount',
            'date',
            'bahasha_card_number',
            'muumini',
            'payment_type_name',
            'jumuiya_details',
            'inserted_at',
            'inserted_by',
        ]

    def get_bahasha_card_number(self, obj):
        if obj.bahasha:
            return obj.bahasha.card_no
        return None

    def get_muumini(self, obj):
        if obj.bahasha and obj.bahasha.mhumini:
            return f"{obj.bahasha.mhumini.first_name} {obj.bahasha.mhumini.last_name}"
        return None

    def get_payment_type_name(self, obj):
        if obj.payment_type:
            return obj.payment_type.name
        return None

    def get_jumuiya_details(self, obj):
        if obj.bahasha and obj.bahasha.mhumini and obj.bahasha.mhumini.jumuiya:
            return obj.bahasha.mhumini.jumuiya.name
        return None


class PaymentTypeTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypeTransfer
        fields = "__all__"


class RevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revenue
        fields = "__all__"


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = "__all__"

    
class ExpenseSerializer(serializers.ModelSerializer):
    expense_category = serializers.PrimaryKeyRelatedField(queryset=ExpenseCategory.objects.all())
    category_details = ExpenseCategorySerializer(source="expense_category", read_only=True)
    class Meta:
        model = Expense
        fields = "__all__"


class MchangoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mchango
        fields = "__all__"


class MchangoPaymentSerializer(serializers.ModelSerializer):
    # mhumini = serializers.PrimaryKeyRelatedField(queryset=Wahumini.objects.all())
    mchango = serializers.PrimaryKeyRelatedField(queryset=Mchango.objects.all())
    mchango_details = MchangoSerializer(source="mchango", read_only=True)
    mhumini_details = WahuminiSerializer(source='mhumini', read_only=True)
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentType.objects.all(), required=False,
                                                      allow_null=True)
    payment_type_details = PaymentTypeSerializer(source='payment_type', read_only=True)
    class Meta:
        model = MchangoPayments
        fields = "__all__"


class AhadiSerializer(serializers.ModelSerializer):
    wahumini = serializers.PrimaryKeyRelatedField(queryset=Wahumini.objects.all())
    mchango = serializers.PrimaryKeyRelatedField(queryset=Mchango.objects.all())
    mchango_details = MchangoSerializer(source="mchango", read_only=True)
    mhumini_details = WahuminiSerializer(source='wahumini', read_only=True)
    class Meta:
        model = Ahadi
        fields = "__all__"



class AhadiPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AhadiPayments
        fields = "__all__"
        #
        # @transaction.atomic
        # def create(self, validated_data):
        #     ahadi_id = self.initial_data.get('ahadi', None)
        #     ahadi_payment_amount = self.initial_data('amount', None)
        #     print("------------------------------------", ahadi_id)
        #
        #     ahadi =  Ahadi.objects.get(id=ahadi_id)
        #     ahadi.paid_amount = ahadi.paid_amount + ahadi_payment_amount
        #
        #     ahadi_payment = AhadiPayments.objects.create(
        #         **validated_data
        #     )
        #
        #     return ahadi_payment

class MavunoSerializer(serializers.ModelSerializer):
    jumuiya = serializers.PrimaryKeyRelatedField(queryset=Jumuiya.objects.all(), required=False, allow_null=True)
    jumuiya_details = JumuiyaSerializer(source='jumuiya', read_only=True)

    class Meta:
        model = Mavuno
        fields = "__all__"


class MavunoPaymentSerializer(serializers.ModelSerializer):
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentType.objects.all(), required=True)
    payment_type_details = PaymentTypeSerializer(source='payment_type', read_only=True)
    mhumini = serializers.PrimaryKeyRelatedField(queryset=Wahumini.objects.all(), required=False, allow_null=True)
    mhumini_details = WahuminiSerializer(source='mhumini', read_only=True)

    class Meta:
        model = MavunoPayments
        fields = "__all__"


class MavunoPaymentsExportSerializer(serializers.ModelSerializer):
    payment_type_name = serializers.SerializerMethodField()
    mhumini_name = serializers.SerializerMethodField()
    mavuno_name = serializers.SerializerMethodField()

    class Meta:
        model = MavunoPayments
        fields = [
            'id',
            'amount',
            'date',
            'payment_type_name',
            'mhumini_name',
            'mavuno_name',
            'inserted_at',
            'inserted_by',
        ]

    def get_payment_type_name(self, obj):
        if obj.payment_type:
            return obj.payment_type.name
        return None

    def get_mhumini_name(self, obj):
        if obj.mhumini:
            return f"{obj.mhumini.first_name} {obj.mhumini.last_name}"
        return None

    def get_mavuno_name(self, obj):
        if obj.mavuno:
            return obj.mavuno.name
        return None



        