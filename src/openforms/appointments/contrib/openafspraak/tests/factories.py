import factory
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory as _ServiceFactory

from ..models import OpenAfspraakConfig


class ServiceFactory(_ServiceFactory):
    api_root = factory.Sequence(lambda n: f"http://www.example{n}.com/api/")
    api_type = APITypes.orc


class OpenAfspraakConfigFactory(factory.django.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)

    class Meta:
        model = OpenAfspraakConfig
