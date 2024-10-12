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
from unittest import TestCase
from wsgi import app
from service.models import Recommendations, DataValidationError, db
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

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

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
