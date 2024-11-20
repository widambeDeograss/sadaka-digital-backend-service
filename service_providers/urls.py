from django.urls import path

from .operations.ahadi_stats import AhadiStats
from .operations.dashboard_stats import ChurchDashboardStatsView
from .operations.matumizi_stats import ExpenseStats
from .operations.mchango_stats import MchangoStats, MchangoStatsView
from .operations.sadaka_zaka_stats import SadakaZakaStats, CheckZakaPresenceView
from .operations.wahumini_stats import WahuminiStatsView
from .views import *
from .views import RevenueUpdateView
from .operations.zaka_sadaka import ZakaMonthlyTotalsView, SadakaWeeklyView

app_name = 'service_providers'

urlpatterns = [
    path('system-package-list-create', SystemPackageListCreateView.as_view(), name="system_package_list_create"),
    path('system-package-retrieve-update-destroy/<int:pk>', SystemPackageRetrieveUpdateDestroyView.as_view(), name="system_package_retrieve_update_destroy"),
    path('system-offer-list-create', SystemOfferListCreateView.as_view(), name="system_offer_list_create"),
    path('system-offer-retrieve-update-destroy/<int:pk>', SystemOfferRetrieveUpdateDestroyView.as_view(), name="system_offer_retrieve_update_destroy"),
    path('get-provider/admin/<uuid:sp_admin_id>/', ServiceProviderByAdminView.as_view(), name='sp_by_admin'),
    path('service-provider-list-create', ServiceProviderListCreateView.as_view(), name="service_provider_list_create"),
    path('service-provider-retrieve-update-destroy/<int:pk>', ServiceProviderRetrieveUpdateDestroyView.as_view(), name="service_provider_retrieve_update_destroy"),
    path('package-list-create', PackageListCreateView.as_view(), name="package_list_create"),
    path('package-retrieve-update-destroy/<int:pk>', PackageRetrieveUpdateDestroyView.as_view(), name="package_retrieve_update_destroy"),
    path('wahumini-list-create', WahuminiListCreateView.as_view(), name="wahumini_list_create"),
    path('wahumini-retrieve-update-destroy/<int:pk>', WahuminiRetrieveUpdateDestroyView.as_view(), name="wahumini_retrieve_update_destroy"),
    path('cards-number-list-create', CardsNumberListCreateView.as_view(), name="cards_number_list_create"),
    path('cards-number-retrieve-update-destroy/<int:pk>', CardsNumberRetrieveUpdateDestroyView.as_view(), name="cards_number_retrieve_update_destroy"),
    path('cards-number-retrieve-by-card-no/<str:card_no>/', CardsNumberRetrieveUpdateDestroyView.as_view(), name="cards_number_retrieve_by_card_no"),
    path('payment-type-list-create', PaymentTypeListCreateView.as_view(), name="payment_type_list_create"),
    path('payment-type-retrieve-update-destroy/<int:pk>', PaymentTypeRetrieveUpdateDestroyView.as_view(), name="payment_type_retrieve_update_destroy"),
    path('sadaka-list-create', SadakaListCreateView.as_view(), name="sadaka_list_create"),
    path('sadaka-retrieve-update-destroy/<int:pk>', SadakaRetrieveUpdateDestroyView.as_view(), name="sadaka_retrieve_update_destroy"),
    path('zaka-list-create', ZakaListCreateView.as_view(), name="zaka_list_create"),
    path('zaka-retrieve-update-destroy/<int:pk>', ZakaRetrieveUpdateDestroyView.as_view(), name="zaka_retrieve_update_destroy"),
    path('payment-type-transfer-list-create', PaymentTypeTransferListCreateView.as_view(), name="payment_type_transfer_list_create"),
    path('payment-type-transfer-retrieve-update-destroy/<int:pk>', PaymentTypeTransferRetrieveUpdateDestroyView.as_view(), name="payment_type_transfer_retrieve_update_destroy"),
    path('revenue-list-create', RevenueListCreateView.as_view(), name="revenue_list_create"),
    path('revenue/update/', RevenueUpdateView.as_view()),
    path('revenue-retrieve-update-destroy/<int:pk>', RevenueRetrieveUpdateDestroyView.as_view(), name="revenue_retrieve_update_destroy"),
    path('expense-list-create', ExpenseListCreateView.as_view(), name="expense_list_create"),
    path('expense-retrieve-update-destroy/<int:pk>', ExpenseRetrieveUpdateDestroyView.as_view(), name="expense_retrieve_update_destroy"),
    path('expense-category-list-create', ExpenseCategoryListCreateView.as_view(), name="expense_category_list_create"),
    path('expense-category-retrieve-update-destroy/<int:pk>', ExpenseCategoryRetrieveUpdateDestroyView.as_view(), name="expense_category_retrieve_update_destroy"),
    path('mchango-list-create', MchangoListCreateView.as_view(), name="mchango_list_create"),
    path('mchango-retrieve-update-destroy/<int:pk>', MchangoRetrieveUpdateDestroyView.as_view(), name="mchango_retrieve_update_destroy"),
    path('mchango-payment-list-create', MchangoPaymentListCreateView.as_view(), name="mchango_payment_list_create"),
    path('mchango-payment-retrieve-update-destroy/<int:pk>', MchangoPaymentListCreateView.as_view(),
         name="mchango_retrieve_update_destroy"),
    path('ahadi-list-create', AhadiListCreateView.as_view(), name="ahadi_list_create"),
    path('ahadi-retrieve-update-destroy/<int:pk>', AhadiRetrieveUpdateDestroyView.as_view(), name="ahadi_retrieve_update_destroy"),
    path('kanda-list-create', KandaViewListCreate.as_view(), name="kanda_list_create"),
    path('kanda-retrieve-update-destroy/<int:pk>', KandaViewUpdateDistroy.as_view(),
         name="kandaa_retrieve_update_destroy"),
    path('jumuiya-list-create', JumuiyaViewListCreate.as_view(), name="jumuiya_list_create"),
    path('jumuiya-retrieve-update-destroy/<int:pk>', JumuiyaViewUpdateDistrol.as_view(),
         name="jumuiyaa_retrieve_update_destroy"),
    path('zaka/monthly-totals/', ZakaMonthlyTotalsView.as_view(), name='zaka-monthly-totals'),
    path('sadaka/monthly-totals/', SadakaWeeklyView.as_view(), name='sadaka-monthly-totals'),
    path('sp-managers/', SpManagerListView.as_view({'get': 'list', 'post':'create'}), name='spmanager-list'),
    path('sp-managers/<int:pk>/', SpManagerDetailView.as_view(), name='spmanager-detail'),
    path('mchango-details/<int:mchango_id>/', MchangoStatsView.as_view(), name='spmanager-detail'),
    path('ahadi-payments', AhadiPaymentListCreateView.as_view(), name='ahadi-payments'),
    path('sadaka-zaka-stats', SadakaZakaStats.as_view(), name='sadaka-stats'),
    path('michango-stats', MchangoStats.as_view(), name='mchango-stats'),
    path('dashboard-stats', ChurchDashboardStatsView.as_view(), name='dashboard-stats'),
    path('ahadi-stats', AhadiStats.as_view(), name='ahadi-stats'),
    path('matumizi-stats', ExpenseStats.as_view(), name='matumizi-stats'),
    path('wahumini-stats', WahuminiStatsView.as_view(), name='wahunini-stats'),
    path('check-zaka/', CheckZakaPresenceView.as_view(), name='check-zaka'),


]