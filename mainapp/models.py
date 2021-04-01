from django.db import models
from django.conf import settings
from django.core.cache import cache


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_all(cls):
        if settings.LOW_CACHE:
            key = 'categories'
            categories = cache.get(key)
            if categories is None:
                categories = cls.objects.all()
                cache.set(key, categories)
            return categories
        else:
            return cls.objects.all()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        cache.delete('categories')


class Product(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='products_images', blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=64, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} | {self.category.name}'
