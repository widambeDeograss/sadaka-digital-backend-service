from rest_framework import serializers
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
        allow_null=True,
        required=False
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


class SadakaSerializer(serializers.ModelSerializer):
    bahasha = serializers.PrimaryKeyRelatedField(queryset=CardsNumber.objects.all(), required=False, allow_null=True)
    bahasha_details = CardsNumberSerializer(source='bahasha', read_only=True)
    class Meta:
        model = Sadaka
        fields = "__all__"
        # depth=2


class ZakaSerializer(serializers.ModelSerializer):
    bahasha = serializers.PrimaryKeyRelatedField(queryset=CardsNumber.objects.all(), required=False, allow_null=True)
    bahasha_details = CardsNumberSerializer(source='bahasha', read_only=True)
    class Meta:
        model = Zaka
        fields = "__all__"


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
    mhumini = serializers.PrimaryKeyRelatedField(queryset=Wahumini.objects.all())
    mchango = serializers.PrimaryKeyRelatedField(queryset=Mchango.objects.all())
    mchango_details = MchangoSerializer(source="mchango", read_only=True)
    mhumini_details = WahuminiSerializer(source='mhumini', read_only=True)
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