from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, F, When, Case, DecimalField, IntegerField

from authapp.models import User
from mainapp.models import Product
from ordersapp.models import OrderItem


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        action_1__time_delta = timedelta(hours=12)
        action_2__time_delta = timedelta(days=1)

        action_1__discount = 0.3
        action_2__discount = 0.15
        action_expired__discount = 0.05

        # условие: заказ был сделан менее 12 часов назад
        action_1__condition = Q(order__updated__lte=F('order__created') + action_1__time_delta)
        # условие: заказ был сделан более 12 часов назад, но менее 1 дня назад
        action_2__condition = Q(order__updated__gt=F('order__created') + action_1__time_delta) & \
                              Q(order__updated__lte=F('order__created') + action_2__time_delta)
        # условие: заказ был сделан более 1 дня назад
        action_expired__condition = Q(order__updated__gt=F('order__created') + action_2__time_delta)

        # если заказ новый, то 1
        action_1__order = When(action_1__condition, then=1)
        # если заказ постарше, то 2
        action_2__order = When(action_2__condition, then=2)
        # если заказ старый (более суток), то 3
        action_expired__order = When(action_expired__condition, then=3)

        # скидка меняется от времени заказа
        # на свежие заказы скидка 30% - 0,3
        action_1__price = When(action_1__condition,
                               then=F('product__price') * F('quantity') * action_1__discount)
        # скидка  15% - 0,15
        action_2__price = When(action_2__condition,
                               then=F('product__price') * F('quantity') * action_2__discount)

        # скидка  5% - 0,05
        action_expired__price = When(action_expired__condition,
                                     then=F('product__price') * F('quantity') * action_expired__discount)

        test_orderss = OrderItem.objects.annotate(
            action_order=Case(
                action_1__order,
                action_2__order,
                action_expired__order,
                output_field=IntegerField(),  # тип результата
            )).annotate(
            total_price=Case(
                action_1__price,
                action_2__price,
                action_expired__price,
                output_field=DecimalField(),  # тип результата
            )).order_by('action_order', 'total_price').select_related()
        # категория заказа: 1, 2, 3
        # total_price - вычисляется в зависимости от скидки
        for orderitem in test_orderss:
            print(f'{orderitem.action_order:2}: заказ №{orderitem.pk:3}:\
                   {orderitem.product.name:15}: скидка\
                   {abs(orderitem.total_price):6.2f} руб. | \
                   {orderitem.order.updated - orderitem.order.created}')
