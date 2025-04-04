from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stocks.views import StockViewSet, WatchlistViewSet
from alerts.views import AlertViewSet
from accounts.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Create a router for our API
router = DefaultRouter()
router.register(r'stocks', StockViewSet)
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
