from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode, urlunparse

import requests
from django.utils import timezone
from social_core.exceptions import AuthForbidden

from authapp.models import ShopUserProfile


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name != 'vk-oauth2':
        return

    # print(response)
    """ response
    {'access_token': 'aa8e63b982e3a5dc60', 
    'expires_in': 86400, 'user_id': 111111, 
    'email': 'aaaa@bbb.ru', 'first_name': 'name', 'id': 11111, 'last_name': 'surname', 
    'screen_name': 'soloninin_anton', 'nickname': '', 
    'photo': 'url', 'user_photo': 'url'}
    """

    # access_token = response['access_token']
    # api_url = f"https://api.vk.com/method/users.get/?fields=bdate,about,sex&access_token={access_token}&v=5.92"

    api_url = urlunparse(('https',
                          'api.vk.com',
                          '/method/users.get',
                          None,
                          urlencode(OrderedDict(fields=','.join(('bdate', 'sex', 'about')),
                                                access_token=response['access_token'],
                                                v='5.92')),
                          None
                          ))

    resp = requests.get(api_url)
    if resp.status_code != 200:
        return

    data = resp.json()
    # print(data)
    """ data = 
    {'response': [{'first_name': 'name', 'id': 1111, 'last_name': 'sur name', 
    'can_access_closed': True, 'is_closed': False, 'sex': 2, 'bdate': '23.02.2000', 'about': '1'}]}
    """
    data = data['response'][0]

    user.email = response['email']
    if data['sex']:
        if data['sex'] == 2:
            user.shopuserprofile.gender = ShopUserProfile.MALE
        elif data['sex'] == 1:
            user.shopuserprofile.gender = ShopUserProfile.FEMALE

    if data['about']:
        user.shopuserprofile.aboutMe = data['about']

    if data['bdate']:
        bdate = datetime.strptime(data['bdate'], '%d.%m.%Y').date()

        age = timezone.now().date().year - bdate.year
        if age < 18:
            user.delete()
            raise AuthForbidden('social_core.backends.vk.VKOAuth2')

    user.save()
