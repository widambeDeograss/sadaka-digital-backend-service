from django.contrib import admin
from .models import (
    CardsNumber, Mchango, PaymentType, ServiceProvider,
    SystemPackage, Zaka, Ahadi, Sadaka, Revenue,
    PaymentTypeTransfer, ExpenseCategory, Expense,
    SystemOffer, Package, Wahumini, Jumuiya, Kanda, MchangoPayments, SadakaTypes, AhadiPayments, MavunoPayments, Mavuno,
    SpManagers
)

# Register all models
admin.site.register(CardsNumber)
admin.site.register(Mchango)
admin.site.register(PaymentType)
admin.site.register(ServiceProvider)
admin.site.register(SystemPackage)
admin.site.register(Zaka)
admin.site.register(Ahadi)
admin.site.register(Sadaka)
admin.site.register(Revenue)
admin.site.register(PaymentTypeTransfer)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(SystemOffer)
admin.site.register(Package)
admin.site.register(Wahumini)
admin.site.register(Kanda)
admin.site.register(Jumuiya)
admin.site.register(SadakaTypes)
admin.site.register(MchangoPayments)
admin.site.register(AhadiPayments)
admin.site.register(MavunoPayments)
admin.site.register(Mavuno)
admin.site.register(SpManagers)