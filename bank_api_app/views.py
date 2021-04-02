from django.contrib.auth.models import User, AnonymousUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.generics import (CreateAPIView,
                                     ListCreateAPIView,
                                     get_object_or_404,
                                     RetrieveDestroyAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Account, Transaction
from .serializers import (UserRegisterSerializer,
                          AccountSerializer,
                          TransactionSerializer,
                          TransactionSerializerWithoutAccount)


class RegisterUserView(CreateAPIView):
    """
    Register API
    creates new user
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'user registered successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)


class AccountViewSet(viewsets.ModelViewSet):
    """
    Account API
    create: Add a new account with the name
    list: Get list of all accounts of user
    retrieve: Get certain account by id
    destroy: Delete certain account by id
    update: Rename certain account
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['name', 'balance']
    ordering_fields = ['name', 'balance']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Account.objects.none()
        return Account.objects.filter(owner=self.request.user)


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    Transaction API
    create: Add a new transaction
    list: Get list of all transactions of user
    retrieve: Get certain transaction by id
    destroy: Delete certain transaction by id
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['account', 'transaction_type', 'date', 'amount', 'comment']
    ordering_fields = ['account', 'transaction_type', 'date', 'amount']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transaction.objects.none()
        accounts_of_current_user = Account.objects.filter(owner=self.request.user)
        return Transaction.objects.filter(account__in=accounts_of_current_user)


class TransactionListCreateAPIView(ListCreateAPIView):
    """
    Transaction connected to account API
    post: Add a new transaction to the chosen account
    get: Get list of all transactions of chosen account
    """
    serializer_class = TransactionSerializerWithoutAccount
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['transaction_type', 'date', 'amount', 'comment']
    ordering_fields = ['transaction_type', 'date', 'amount']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transaction.objects.none()
        accounts_of_current_user = Account.objects.filter(owner=self.request.user)
        return Transaction.objects.filter(account__in=accounts_of_current_user).filter(
            account__id=self.kwargs['account_pk'])

    def perform_create(self, serializer):
        account = get_object_or_404(Account, pk=self.kwargs['account_pk'])
        return serializer.save(account=account)


class TransactionRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    """
    Transaction connected to account API
    get: Get a certain transaction of the chosen account by id
    delete: Delete a certain transaction of the chosen account by id
    """

    serializer_class = TransactionSerializerWithoutAccount
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'transaction_pk'

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transaction.objects.none()
        accounts_of_current_user = Account.objects.filter(owner=self.request.user)
        return Transaction.objects.filter(account__in=accounts_of_current_user).filter(
            account__id=self.kwargs['account_pk'])
