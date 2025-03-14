from django.urls import path, include
from .operations.ahadi_stats import AhadiStats
from .operations.dashboard_stats import ChurchDashboardStatsView
from .operations.matumizi_stats import ExpenseStats
from .operations.mavuno_stats import MavunoStatsAndChartView
from .operations.mchango_stats import MchangoStats, MchangoStatsView
from .operations.sadaka_zaka_stats import SadakaZakaStats, CheckZakaPresenceView
from .operations.send_dedicated_message import SendDedicatedMessage
from .operations.wahumini_stats import WahuminiStatsView
from .reports.expences import ExpenseReportView
from .reports.payment_type_revenue import RevenueByPaymentTypeView
from .reports.revenue import RevenueReportView
from .reports.wahumini import MuhuminiContributionsView
from .views import *
from .operations.zaka_sadaka import ZakaMonthlyTotalsView, SadakaWeeklyView
from  .operations.revenue import MonthlyReportViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'revenue-reports', MonthlyReportViewSet, basename='revenue-reports')
# router.register(r'wahumini-statement', MuhuminiContributionsView, basename='statement')

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
    path('sadaka--type-retrieve-update-destroy/<int:pk>', SadakaTypeRetrieveUpdateDestroyView.as_view(),
         name="sadaka_type_retrieve_update_destroy"),
    path('sadaka-type-list-create', SadakaTypeListCreateView.as_view(), name="sadaka_type_list_create"),
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
    path('create-sp-manager', CreateSpManager.as_view()),
    path('sp-managers/', SpManagerListView.as_view({'get': 'list', 'post':'create'}), name='spmanager-list'),
    path('sp-managers/<int:pk>/', SpManagerDetailView.as_view(), name='spmanager-detail'),
    path('mchango-details/<int:mchango_id>/', MchangoStatsView.as_view(), name='spmanager-detail'),
    path('ahadi-payments', AhadiPaymentListCreateView.as_view(), name='ahadi-payments'),
    path('sadaka-zaka-stats', SadakaZakaStats.as_view(), name='sadaka-stats'),
    path('michango-stats', MchangoStats.as_view(), name='mchango-stats'),
    path('dashboard-stats', ChurchDashboardStatsView.as_view(), name='dashboard-stats'),
    path('ahadi-stats', AhadiStats.as_view(), name='ahadi-stats'),
    # path('revenue-reports/', MonthlyReportViewSet.as_view({'get'}), name='revenue-stats'),
    path('matumizi-stats', ExpenseStats.as_view(), name='matumizi-stats'),
    path('check-zaka/', CheckZakaPresenceView.as_view(), name='check-zaka'),
    path('wahumini-stats', WahuminiStatsView.as_view(), name='wahunini-stats'),
    path('mavuno/stats-and-chart/', MavunoStatsAndChartView.as_view(), name="mavuno_list_create"),
    path('mavuno-list-create', MavunoListCreateView.as_view(), name="mavuno_list_create"),
    path('mavuno-retrieve-update-destroy/<int:pk>', MavunoRetrieveUpdateDestroyView.as_view(), name="mavuno_retrieve_update_destroy"),
    path('mavuno-payment-list-create', MavunoPaymentListCreateView.as_view(), name="mavuno_payment_list_create"),
    path('mavuno-payment-retrieve-update-destroy/<int:pk>', MavunoPaymentRetrieveUpdateDestroyView.as_view(), name="mavuno_payment_retrieve_update_destroy"),
    path('reports/wahumini-statement', MuhuminiContributionsView.as_view(), ),
    path('reports/revenue-statement', RevenueReportView.as_view(), ),
    path('reports/expenses-statement', ExpenseReportView.as_view(), ),
    path('sms/send-custom', SendDedicatedMessage.as_view(), ),
    path('reports/', include(router.urls)),
    path('revenue/<int:church_id>/', RevenueByPaymentTypeView.as_view(), name='revenue_by_payment_type')
]