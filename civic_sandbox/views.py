
from rest_framework.decorators import api_view
from django.contrib.gis.geos import GEOSGeometry, MultiPoint, MultiPolygon, MultiLineString
from .models import Permit
from .serializers import PermitSerializer
from .helpers import sandbox_view_factory
from .meta import permits_meta 



permits = sandbox_view_factory(
  model_class=Permit,
  serializer_class=PermitSerializer,
  multi_geom_class=MultiPoint,
  geom_field='point',
  attributes =permits_meta['attributes'],
  dates=permits_meta['dates'],
  )
