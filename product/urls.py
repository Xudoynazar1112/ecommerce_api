from django.urls import path, include
from rest_framework.routers import DefaultRouter
from product.services import FlashSaleListCreateView, check_flash_sale, ProductViewHistoryCreate, admin_replenish_stock
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('sale/', FlashSaleListCreateView.as_view(), name='sale'),
    path('check-sale/<int:product_id>/', check_flash_sale, name='product-view-history-create'),
    path('product-view/', ProductViewHistoryCreate.as_view(), name='product-view-history-create'),
    path('admin/replenish_stock/<int:product_id>/<int:amount>', admin_replenish_stock, name='admin_replenish_stock'),
]