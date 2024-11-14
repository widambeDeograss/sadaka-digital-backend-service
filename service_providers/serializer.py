from django.db import transaction
from rest_framework import serializers

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
    sp_manager = UserSerializer(read_only=True)
    # sp_manager = serializers.CharField()

    class Meta:
        model = SpManagers
        fields = ['id', 'sp_manager', 'church', 'inserted_by', 'deleted']
        extra_kwargs = {
            'sp_manager': {
                'validators': []
            }
        }

    @transaction.atomic
    def create(self, validated_data):
        try:
            user_data = self.initial_data.get('sp_manager', None)
            print("------------------------------------", user_data)

            # Create the user with the correct role
            user = UserSerializer().create(user_data)

            # Check if this user is already a manager for another church
            if SpManagers.objects.filter(
                    sp_manager=user,
                    deleted=False
            ).exists():
                raise serializers.ValidationError({
                    "sp_manager": "This user is already a manager of another church"
                })

            # Check if the church already has the maximum number of managers
            existing_managers = SpManagers.objects.filter(
                church=validated_data['church'],
                deleted=False
            ).count()
            max_managers = 5
            if existing_managers >= max_managers:
                raise serializers.ValidationError({
                    "church": f"This church already has the maximum number of managers ({max_managers})"
                })

            # Create the SpManager record
            sp_manager = SpManagers.objects.create(
                sp_manager=user,
                **validated_data
            )

            return sp_manager

        except Exception as e:
            raise serializers.ValidationError({
                "error": f"Failed to create manager: {str(e)}"
            })

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'sp_manager' in validated_data:
            user_data = validated_data.pop('sp_manager')
            user = instance.sp_manager

            # Update user fields
            for attr, value in user_data.items():
                if attr != 'password':
                    setattr(user, attr, value)
                else:
                    user.set_password(value)

            user.save()

        # Update SpManager fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


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
    jumuiya = serializers.PrimaryKeyRelatedField(
        queryset=Jumuiya.objects.all(),
        allow_null=True,
        required=False
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


class SadakaSerializer(serializers.ModelSerializer):
    bahasha = serializers.PrimaryKeyRelatedField(queryset=CardsNumber.objects.all(), required=False, allow_null=True)
    bahasha_details = CardsNumberSerializer(source='bahasha', read_only=True)
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentType.objects.all(), required=False, allow_null=True)
    payment_type_details = PaymentTypeSerializer(source='payment_type', read_only=True)
    class Meta:
        model = Sadaka
        fields = "__all__"
        # depth=2


class ZakaSerializer(serializers.ModelSerializer):
    bahasha = serializers.PrimaryKeyRelatedField(queryset=CardsNumber.objects.all(), required=False, allow_null=True)
    bahasha_details = CardsNumberSerializer(source='bahasha', read_only=True)
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentType.objects.all(), required=False, allow_null=True)
    payment_type_details = PaymentTypeSerializer(source='payment_type', read_only=True)
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

