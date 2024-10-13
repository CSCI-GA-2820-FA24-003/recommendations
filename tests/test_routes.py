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
TestRecommendations API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Recommendations
from .factories import RecommendationsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendations).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create recommendations
    ############################################################

    def _create_recommendations(self, count: int = 1) -> list:
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationsFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test recommendation",
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    # T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_recommendation = RecommendationsFactory()
        logging.debug("Test Recommendation: %s", test_recommendation.serialize())
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_recommendation = response.get_json()
        self.assertEqual(
            new_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertEqual(
            new_recommendation["recommended_id"], test_recommendation.recommended_id
        )
        self.assertEqual(
            new_recommendation["recommendation_type"],
            test_recommendation.recommendation_type,
        )

        # Todo: uncomment this code when get_recommendations is implemented
        # # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_recommendation = response.get_json()
        # self.assertEqual(
        #     new_recommendation["product_id"], test_recommendation.product_id
        # )
        # self.assertEqual(
        #     new_recommendation["recommended_id"], test_recommendation.recommended_id
        # )
        # self.assertEqual(new_recommendation["recommendation_type"], test_recommendation.recommendation_type)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------

    def test_get_recommendation(self):
        """It should Get a single Recommendation"""
        # get the id of a recommendation
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_recommendation.id)

    def test_get_recommendation_not_found(self):
        """It should not Get a Recommendation thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_recommendation_list(self):
        """It should Get a list of recommendations"""
        self._create_recommendations(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
