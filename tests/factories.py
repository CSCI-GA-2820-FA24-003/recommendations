"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice
from service.models import Recommendations


class RecommendationsFactory(factory.Factory):
    """Creates fake recommendations"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Recommendations

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n + 1)
    recommended_id = factory.Sequence(lambda n: n + 100)
    status = FuzzyChoice(choices=["active", "expired", "draft"])
    recommendation_type = FuzzyChoice(choices=["cross-sell", "up-sell", "accessory"])
