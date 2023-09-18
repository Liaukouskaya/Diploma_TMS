from django.conf.urls.static import static, settings
from django.urls import path
from . import views


urlpatterns = [

    path('', views.search, name='search'),
    path('result-<str:text_search>', views.search_result, name='search_result'),
    path('result/people-<str:text_search>', views.search_result_people, name='search_result_people'),
    path('result/group-<str:text_search>', views.search_result_group, name='search_result_group'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


