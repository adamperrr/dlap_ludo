from django.urls import include, path
from django.contrib import admin
from rest_framework import routers
from dlap_ludo.game import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('game/create_room/', views.create_room, name='create_room'),
    path('game/join_room/', views.join_room, name='join_room'),

    path('admin/', admin.site.urls)
]
