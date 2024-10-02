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
    class Meta:
        model = Package
        fields = "__all__"


class WahuminiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wahumini
        fields = "__all__"


class CardsNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardsNumber
        fields = "__all__"


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = "__all__"


class SadakaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sadaka
        fields = "__all__"


class ZakaSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Expense
        fields = "__all__"


class MchangoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mchango
        fields = "__all__"


class AhadiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ahadi
        fields = "__all__"