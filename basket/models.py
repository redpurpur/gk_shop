from datetime import timedelta
from django.db import models
from django.utils.timezone import now

from authapp.models import User
from mainapp.models import Product


class BasketQuerySet(models.QuerySet):

    def count_gt_2(self):
        return self.filter(quantity__gt=2)

    def count_lt_2(self):
        return self.filter(quantity__lt=2)

    def delete(self):
        for object in self:
            object.refresh_quantity()
        super().delete()

    def delete_old_baskets(self):
        self.filter(created_timestamp_lt=now() - timedelta(hours=24)).delete()


class Basket(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    objects = BasketQuerySet.as_manager()

    def __str__(self):
        return f'Корзина для {self.user.username} | Продукт {self.product.name}'

    def sum(self):
        return self.quantity * self.product.price

    def total_quantity(self):
        baskets = Basket.objects.filter(user=self.user)
        return sum(basket.quantity for basket in baskets)

    def total_sum(self):
        baskets = Basket.objects.filter(user=self.user)
        return sum(basket.sum() for basket in baskets)

    def delete(self, using=None, keep_parents=False):
        self.product.quantity += self.quantity
        self.product.save()

        super().delete()

    def refresh_quantity(self):
        if self.pk:
            self.product.quantity -= self.quantity - Basket.objects.get(pk=self.pk).quantity
        else:
            self.product.quantity -= self.quantity
        self.product.save()

    def save(self, *args):
        self.refresh_quantity()
        super().save(*args)
