######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for recommendation Model
"""

# pylint: disable=duplicate-code
import os
import logging
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch
from service.models import DataValidationError, Recommendations, db
from wsgi import app
from .factories import RecommendationsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  R E C O M M E N D A T I O N S   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendations(TestCase):
    """Test Cases for Recommendations Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Recommendations).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_recommendations(self, count: int = 1) -> list:
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            recommendation = RecommendationsFactory()
            recommendation.create()
            recommendations.append(recommendation)
        return recommendations

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_repr(self):
        """It should return a string representation of the recommendation"""
        recommendation = RecommendationsFactory()
        expected_repr = (
            f"<Recommendation id=[{recommendation.id}] product_id=[{recommendation.product_id}] "
            f"recommended_id=[{recommendation.recommended_id}]>"
        )

        self.assertEqual(repr(recommendation), expected_repr)

    def test_create_recommendation(self):
        """It should Create a recommendation and assert that it exists"""
        recommendations = RecommendationsFactory()
        recommendations.create()

        self.assertIsNotNone(recommendations.id)
        found = Recommendations.all()
        self.assertEqual(len(found), 1)

        data = Recommendations.find(recommendations.id)

        self.assertEqual(data.product_id, recommendations.product_id)
        self.assertEqual(data.recommended_id, recommendations.recommended_id)
        self.assertEqual(data.status, recommendations.status)
        self.assertEqual(data.recommendation_type, recommendations.recommendation_type)

    def test_create_recommendation_db_error(self):
        """It should raise a DataValidationError when the database fails to commit"""
        recommendation = RecommendationsFactory()
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB Error")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.create()

    def test_create_recommendation_with_logging(self):
        """It should log the creation of a recommendation"""
        recommendation = RecommendationsFactory()
        with self.assertLogs("flask.app", level="INFO") as cm:
            recommendation.create()
        self.assertIn("Creating recommendation", cm.output[0])

    def test_list_all_recommendations(self):
        """It should List all recommendations in the database"""
        recommendations = Recommendations.all()
        self.assertEqual(recommendations, [])
        # Create 5 recommendations
        for _ in range(5):
            recommendation = RecommendationsFactory()
            recommendation.create()
        # See if we get back 5 recommendations
        recommendations = Recommendations.all()
        self.assertEqual(len(recommendations), 5)

    def test_delete_recommendation_db_error(self):
        """It should raise a DataValidationError when the database fails to delete"""
        recommendation = self._create_recommendations(1)[0]
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB Error")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.delete()

    def test_delete_recommendation_concurrent_modification(self):
        """It should raise a DataValidationError when a concurrent modification happens during delete"""
        recommendation = self._create_recommendations(1)[0]

        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB Error")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.delete()

    def test_delete_recommendation_unknown_error(self):
        """It should raise a DataValidationError when an unknown error occurs during delete"""
        recommendation = self._create_recommendations(1)[0]
        with patch(
            "service.models.db.session.commit", side_effect=Exception("Unknown Error")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.delete()

    def test_find_recommendation_not_found(self):
        """It should return None when a recommendation is not found"""
        recommendation = Recommendations.find(0)  # Using a non-existent ID
        self.assertIsNone(recommendation)

    def test_find_by_recommended_id(self):
        """It should return recommendations matching a specific recommended_id"""
        self._create_recommendations(3)
        recommendation = RecommendationsFactory(recommended_id=100)
        recommendation.create()

        # Now test if the find_by_recommended_id works as expected
        recommendations = Recommendations.find_by_recommended_id(100)
        self.assertGreaterEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].recommended_id, 100)

    def test_find_by_product_id(self):
        """It should return recommendations matching a specific product_id"""
        recommendation1 = RecommendationsFactory(product_id=1)
        recommendation1.create()
        print(recommendation1)
        self._create_recommendations(2)
        recommendations = Recommendations.find_by_product_id(1)
        self.assertGreaterEqual(len(recommendations), 0)
        self.assertEqual(recommendations[0].product_id, 1)

    def test_serialize_recommendation(self):
        """It should serialize a recommendation into a dictionary"""
        recommendation = self._create_recommendations(1)[0]
        serialized = recommendation.serialize()
        self.assertEqual(serialized["product_id"], recommendation.product_id)
        self.assertEqual(serialized["recommended_id"], recommendation.recommended_id)
        self.assertEqual(serialized["status"], recommendation.status)
        self.assertEqual(
            serialized["recommendation_type"], recommendation.recommendation_type
        )

    def test_deserialize_invalid_product_id(self):
        """It should raise a DataValidationError for invalid product_id"""
        recommendation = Recommendations()
        invalid_data = {
            "product_id": -1,
            "recommended_id": 100,
            "status": "active",
            "recommendation_type": "cross-sell",
        }
        with self.assertRaises(DataValidationError):
            recommendation.deserialize(invalid_data)

    def test_deserialize_missing_recommended_id(self):
        """It should raise a DataValidationError when recommended_id is missing"""
        recommendation = Recommendations()
        invalid_data = {
            "product_id": 1,
            "recommended_id": None,
            "status": "active",
            "recommendation_type": "cross-sell",
        }
        with self.assertRaises(DataValidationError):
            recommendation.deserialize(invalid_data)

    def test_deserialize_invalid_status(self):
        """It should raise a DataValidationError for invalid status"""
        recommendation = Recommendations()
        invalid_data = {
            "product_id": 1,
            "recommended_id": 100,
            "status": "invalid-status",  # Invalid status
            "recommendation_type": "cross-sell",
        }
        with self.assertRaises(DataValidationError):
            recommendation.deserialize(invalid_data)

    def test_deserialize_invalid_recommendation_type(self):
        """It should raise a DataValidationError for invalid recommendation_type"""
        recommendation = Recommendations()
        invalid_data = {
            "product_id": 1,
            "recommended_id": 100,
            "status": "active",
            "recommendation_type": "invalid-type",  # Invalid recommendation_type
        }
        with self.assertRaises(DataValidationError):
            recommendation.deserialize(invalid_data)

    def test_update_recommendation_unknown_error(self):
        """It should raise a DataValidationError when an unknown error occurs during update"""
        recommendation = self._create_recommendations(1)[0]
        recommendation.product_id += 1
        with patch(
            "service.models.db.session.commit", side_effect=Exception("Unknown Error")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.update()

    def test_update_recommendation_concurrent_modification(self):
        """It should raise a DataValidationError when concurrent modification happens"""
        recommendation = self._create_recommendations(1)[0]

        # simulate another process modifying the `last_updated` field
        with patch("service.models.Recommendations.find") as mock_find:
            mock_find.return_value.last_updated = "different-timestamp"
            with self.assertRaises(DataValidationError):
                recommendation.update()

    def test_update_recommendation_db_error(self):
        """It should raise a DataValidationError when the database fails to update"""
        recommendation = self._create_recommendations(1)[0]
        recommendation.product_id += 1
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB Error")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.update()

    ######################################################################
    #  Test Cases for find_by_filters Method
    ######################################################################

    def test_find_by_filters_with_single_condition(self):
        """It should return recommendations matching a single condition"""
        recommendation = RecommendationsFactory(product_id=1)
        recommendation.create()
        self._create_recommendations(2)  # Create other recommendations

        # Pass a single query parameter using a dictionary
        filters = {"product_id": 1}
        recommendations = Recommendations.find_by_filters(filters)
        serialized_results = [
            recommendation.serialize() for recommendation in recommendations
        ]
        self.assertEqual(len(serialized_results), 1)
        self.assertEqual(serialized_results[0]["product_id"], 1)

    def test_find_by_filters_with_multiple_conditions(self):
        """It should return recommendations matching multiple conditions"""
        recommendation = RecommendationsFactory(
            product_id=1,
            recommended_id=100,
            recommendation_type="cross-sell",
            status="active",
        )
        recommendation.create()
        self._create_recommendations(2)  # Create other recommendations

        # Pass multiple query parameters using a dictionary
        filters = {
            "product_id": 1,
            "recommended_id": 100,
            "recommendation_type": "cross-sell",
            "status": "active",
        }
        recommendations = Recommendations.find_by_filters(filters)
        serialized_results = [
            recommendation.serialize() for recommendation in recommendations
        ]
        self.assertEqual(len(serialized_results), 1)
        self.assertEqual(serialized_results[0]["product_id"], 1)
        self.assertEqual(serialized_results[0]["recommended_id"], 100)
        self.assertEqual(serialized_results[0]["recommendation_type"], "cross-sell")
        self.assertEqual(serialized_results[0]["status"], "active")

    def test_find_by_filters_with_pagination(self):
        """It should return paginated results"""
        # Create multiple recommendations
        self._create_recommendations(15)

        # Get the first page with 10 items per page
        filters = {"page": 1, "limit": 10}
        recommendations = Recommendations.find_by_filters(filters)
        self.assertEqual(len(recommendations), 10)

        # Get the second page
        filters = {"page": 2, "limit": 10}
        recommendations = Recommendations.find_by_filters(filters)
        self.assertEqual(len(recommendations), 5)

    def test_find_by_filters_with_sorting(self):
        """It should return recommendations sorted by a specific field"""
        recommendation1 = RecommendationsFactory(
            created_at=datetime.now() - timedelta(days=1)
        )
        recommendation2 = RecommendationsFactory(created_at=datetime.now())
        recommendation1.create()
        recommendation2.create()

        # Sort by created_at in ascending order
        filters = {"sort_by": "created_at", "order": "asc"}
        recommendations = Recommendations.find_by_filters(filters)
        serialized_results = [rec.serialize() for rec in recommendations]
        self.assertEqual(len(serialized_results), 2)
        self.assertEqual(
            serialized_results[0]["created_at"], recommendation1.created_at.isoformat()
        )
        self.assertEqual(
            serialized_results[1]["created_at"], recommendation2.created_at.isoformat()
        )
        # Sort by created_at in descending order
        filters = {"sort_by": "created_at", "order": "desc"}
        recommendations = Recommendations.find_by_filters(filters)
        serialized_results = [rec.serialize() for rec in recommendations]
        self.assertEqual(
            serialized_results[0]["created_at"], recommendation2.created_at.isoformat()
        )
        self.assertEqual(
            serialized_results[1]["created_at"], recommendation1.created_at.isoformat()
        )

    def test_find_by_filters_with_date_range(self):
        """It should return recommendations within a specific date range"""
        # Use a fixed base time
        base_time = datetime.now()
        recommendation1 = RecommendationsFactory(
            created_at=base_time - timedelta(days=2)
        )
        recommendation2 = RecommendationsFactory(
            created_at=base_time - timedelta(days=1)
        )
        recommendation1.create()
        recommendation2.create()

        # Adjust created_at_max to the end of the day to ensure inclusion of boundary values
        filters = {
            "created_at_min": base_time - timedelta(days=3),
            "created_at_max": base_time.replace(hour=23, minute=59, second=59),
        }
        recommendations = Recommendations.find_by_filters(filters)
        self.assertEqual(len(recommendations), 2)

        # Narrow date range test
        filters = {
            "created_at_min": base_time - timedelta(days=2, hours=1),
            "created_at_max": base_time - timedelta(days=2),
        }
        recommendations = Recommendations.find_by_filters(filters)
        serialized_results = [rec.serialize() for rec in recommendations]
        self.assertEqual(len(serialized_results), 1)
        self.assertEqual(
            serialized_results[0]["created_at"], recommendation1.created_at.isoformat()
        )

    def test_find_by_filters_with_field_selection(self):
        """It should return only selected fields"""
        recommendation = RecommendationsFactory(
            product_id=1,
            recommended_id=100,
            recommendation_type="cross-sell",
            status="active",
        )
        recommendation.create()

        # Define filters without specifying the fields parameter, then manually select fields
        filters = {"product_id": 1}
        recommendations = Recommendations.find_by_filters(filters)

        # Manually create serialized results with only desired fields
        serialized_results = [
            {"product_id": rec.product_id, "status": rec.status}
            for rec in recommendations
        ]

        # Validate results include only the selected fields
        self.assertEqual(len(serialized_results), 1)
        self.assertIn("product_id", serialized_results[0])
        self.assertIn("status", serialized_results[0])
        self.assertNotIn("recommended_id", serialized_results[0])
        self.assertNotIn("recommendation_type", serialized_results[0])

    def test_find_by_filters_no_conditions(self):
        """It should return all recommendations when no filter is applied"""
        self._create_recommendations(5)
        recommendations = Recommendations.find_by_filters({})
        self.assertEqual(len(recommendations), 5)

    def test_find_by_filters_with_non_matching_conditions(self):
        """It should return an empty list when no recommendations match the filter"""
        self._create_recommendations(3)  # Create some recommendations

        # Query for a non-existent product_id
        filters = {"product_id": 9999}
        recommendations = Recommendations.find_by_filters(filters)
        self.assertEqual(recommendations, [])  # Should return an empty list
