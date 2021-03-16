
def user_status(request):
    print('111')
    user = request.user
    if user.is_authenticated:
        status = '<h1>авторизован</h1>'
    else:
        status = '<h1>не авторизован</h1>'

    return {'status': status}
