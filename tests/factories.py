"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Recommendations


class RecommendationsFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Recommendations

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    recommended_id = factory.Sequence(lambda n: n + 100)
    status = FuzzyChoice(choices=["active", "expired", "draft"])
    type = FuzzyChoice(choices=["cross-sell", "up-sell", "accessory"])

    # Todo: Add your other attributes here...
