from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, F
from authapp.models import User
from mainapp.models import Product


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        # Q - Query
        # | - or
        # & - and
        # ~ - not
        price_lower_1000 = Q(price__lt=1000)  # цена меньше 1000
        not_hoodi = ~Q(name__startswith='Худи')  # имя не начинается с 'Худи'

        # можно комбинировать
        price_lower_1000 | not_hoodi  # не худи или цена меньше 1000
        price_lower_1000 & not_hoodi  # не худи и цена меньше 1000, два условия

        # добавлять в filter, exclude, get по необходимости
        Product.objects.filter( price_lower_1000 | not_hoodi ).all()
