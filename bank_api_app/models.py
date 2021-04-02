from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Account(models.Model):
    name = models.CharField(max_length=50)
    balance = models.DecimalField(validators=[MinValueValidator(0)], max_digits=10, decimal_places=2, default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'owner']


class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        WITHDRAWAL = 'W', 'withdrawal'
        REFILL = 'R', 'refill'

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        'transaction type',
        max_length=1,
        choices=TransactionType.choices,
    )
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(validators=[MinValueValidator(0)], max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
