from django.shortcuts import render


def error_404_view(request, exception):

    """404 страница"""

    user = f'{request.user.first_name} {request.user.last_name}'

    data = {
        'user': user,
    }

    return render(request, '404.html', data, status=404)



