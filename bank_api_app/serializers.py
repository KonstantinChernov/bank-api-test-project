from django.contrib.auth.models import User
from django.db.models import F
from rest_framework import serializers

from bank_api_app.models import Account, Transaction


class UserRegisterSerializer(serializers.ModelSerializer):
    """ Serializer for registration """
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']

    def save(self, *args, **kwargs):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({password: "password does not match"})
        user.set_password(password)
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):
    """ Serializer for accounts """
    class Meta:
        model = Account
        fields = ('id', 'name', 'balance')
        read_only_fields = ('balance',)

    def create(self, validated_data):
        name = self.validated_data['name']
        owner = self.context['request'].user
        if self.Meta.model.objects.filter(owner=owner, name=name).exists():
            raise serializers.ValidationError({'name': ['The account with such name already exists']})
        return Account.objects.create(name=name, owner=owner)

    def update(self, instance, validated_data):
        if self.Meta.model.objects.filter(owner=self.context['request'].user,
                                          name=self.validated_data['name']).exists():
            raise serializers.ValidationError({'name': ['The account with such name already exists']})
        else:
            instance.name = validated_data.get('name', instance.name)
            instance.save()
        return instance


class TransactionSerializer(serializers.ModelSerializer):
    """ Serializer for transactions """
    account = serializers.SlugRelatedField(slug_field='name',
                                           queryset=Account.objects.all())

    class Meta:
        model = Transaction
        fields = ('id', 'account', 'transaction_type', 'date', 'amount', 'comment')
        read_only_fields = ('date',)

    def create(self, validated_data):

        transaction_type = validated_data['transaction_type']
        amount = validated_data['amount']
        account = Account.objects.get(name=validated_data['account'],
                                      owner=self.context['request'].user)
        if amount <= 0:
            raise serializers.ValidationError({'amount': ['amount should be greater then 0']})
        if transaction_type == 'W':
            if amount > account.balance:
                raise serializers.ValidationError({'amount': ['insufficient funds in the account']})
            else:
                account.balance = F('balance') - amount
                account.save()
        elif transaction_type == 'R':
            account.balance = F('balance') + amount
            account.save()

        return Transaction.objects.create(**validated_data)


class TransactionSerializerWithoutAccount(TransactionSerializer):
    """ Serializer for transactions connected to accounts """
    account = serializers.SlugRelatedField(slug_field='name', read_only=True)
