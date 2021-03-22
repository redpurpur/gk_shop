from basket.models import Basket


def basket_count(request):
    user = request.user
    if user.is_authenticated:
        counter = Basket.objects.filter(user=user).count()
    else:
        counter = 0

    return {'basket_count': counter}
