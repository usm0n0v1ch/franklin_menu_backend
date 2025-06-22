# urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from menu.views import CategoryViewSet, ProductViewSet, TableViewSet, OrderViewSet, OptionTypeViewSet, OptionViewSet, \
    OrderItemViewSet, TableFromTokenView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'tables', TableViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'option-types', OptionTypeViewSet)
router.register(r'options', OptionViewSet)
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
urlpatterns = [
    path("table-from-token/<str:token>/", TableFromTokenView.as_view()),

    path('', include(router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
