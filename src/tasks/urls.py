from rest_framework.routers import SimpleRouter

from . import api

router = SimpleRouter()
router.register(r'', api.TasksViewSet)

urlpatterns = router.urls
