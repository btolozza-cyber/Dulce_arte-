from rest_framework.routers import DefaultRouter
from .views import DespachoViewSet

router = DefaultRouter()
router.register('despachos', DespachoViewSet, basename='despacho')

urlpatterns = router.urls