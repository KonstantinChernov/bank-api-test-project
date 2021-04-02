from django.urls import path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from bank_api_app.views import (RegisterUserView,
                                AccountViewSet,
                                TransactionViewSet,
                                TransactionListCreateAPIView,
                                TransactionRetrieveDestroyAPIView)
from bank_api_app.yasg import schema_view

urlpatterns = [
    path('', schema_view.with_ui('swagger')),
    path('login/', views.obtain_auth_token, name='login'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('accounts/<int:account_pk>/transactions/', TransactionListCreateAPIView.as_view(),
         name='account-transactions-list'),
    path('accounts/<int:account_pk>/transactions/<int:transaction_pk>', TransactionRetrieveDestroyAPIView.as_view(),
         name='account-transactions-detail')
]

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns += router.urls
