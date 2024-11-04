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
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
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

    # ----------------------------------------------------------
    # TEST ROOT ROUTE
    # ----------------------------------------------------------
    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Recommendation REST API Service")
        self.assertEqual(data["version"], "1.0")

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
        self.assertEqual(new_recommendation["like"], test_recommendation.like)
        self.assertEqual(new_recommendation["dislike"], test_recommendation.dislike)

    def test_create_recommendation_data_validation_error(self):
        """It should return 400 Bad Request when data validation fails"""
        # Simulate invalid data that will trigger a DataValidationError
        invalid_data = {
            "product_id": "invalid",  # Non-integer value for product_id
            "recommended_id": 101,
            "recommendation_type": "up-sell",
            "status": "active",
            "like": 0,
            "dislike": 0,
        }

        # Send POST request with invalid data
        response = self.client.post(BASE_URL, json=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the actual error message
        data = response.get_json()
        self.assertIn("Invalid product_id: must be an integer", data["message"])

    def test_create_recommendation_db_error(self):
        """It should return 500 Internal Server Error when the database fails"""
        # Simulate a SQLAlchemyError during the database interaction
        test_recommendation = RecommendationsFactory()
        with patch(
            "service.models.Recommendations.create",
            side_effect=SQLAlchemyError("Database error"),
        ):
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            # Check that the error message is correct
            data = response.get_json()
            self.assertIn("Database error occurred", data["message"])

    def test_create_recommendation_missing_content_type(self):
        """It should return 415 Unsupported Media Type when Content-Type is missing"""
        test_recommendation = RecommendationsFactory()
        response = self.client.post(BASE_URL, data=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    def test_create_recommendation_invalid_content_type(self):
        """It should return 415 Unsupported Media Type when Content-Type is invalid"""
        test_recommendation = RecommendationsFactory()
        response = self.client.post(
            BASE_URL, data=test_recommendation.serialize(), content_type="text/plain"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    def test_create_recommendation_unexpected_error(self):
        """It should return 500 Internal Server Error when an unexpected error occurs"""
        # Simulate unexpected error by raising an exception in the create() method
        test_recommendation = RecommendationsFactory()
        original_create = Recommendations.create
        Recommendations.create = lambda self: (_ for _ in ()).throw(
            Exception("Unexpected error")
        )

        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        Recommendations.create = original_create

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
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print(
            f"Response status code: {response.status_code}, Response data: {response.data}"
        )

    def test_delete_non_existing_recommendation(self):
        """It should Delete a Recommendation even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_delete_recommendation_db_error(self):
        """It should return 500 Internal Server Error when a database error occurs during delete"""
        test_recommendation = self._create_recommendations(1)[0]

        # Simulate a SQLAlchemyError during the delete process
        with patch(
            "service.models.Recommendations.delete",
            side_effect=SQLAlchemyError("Database error"),
        ):
            response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            # Check that the correct error message is returned
            data = response.get_json()
            self.assertIn("Database error occurred", data["message"])

    def test_delete_recommendation_unexpected_error(self):
        """It should return 500 Internal Server Error when an unexpected error occurs during delete"""
        test_recommendation = self._create_recommendations(1)[0]

        # Simulate a generic Exception during the delete process
        with patch(
            "service.models.Recommendations.delete",
            side_effect=Exception("Unexpected error"),
        ):
            response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            # Check that the correct error message is returned
            data = response.get_json()
            self.assertIn("An unexpected error occurred", data["message"])

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

    def test_get_all_recommendations(self):
        """It should get all recommendations without filtering by product_id or recommended_id"""
        self._create_recommendations(3)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)

    def test_list_recommendations_invalid_product_id(self):
        """It should not list recommendations with an invalid product_id"""
        response = self.client.get(f"{BASE_URL}?product_id=invalid")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid product_id", data["message"])

    def test_list_recommendations_invalid_recommended_id(self):
        """It should not list recommendations with an invalid recommended_id"""
        response = self.client.get(f"{BASE_URL}?recommended_id=invalid")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid recommended_id", data["message"])

    def test_list_recommendations_by_product_id(self):
        """It should List recommendations by product_id"""
        # Create a recommendation with a specific product_id
        test_recommendation = self._create_recommendations(1)[0]
        product_id = test_recommendation.product_id

        # Send request to list recommendations by product_id
        response = self.client.get(f"{BASE_URL}?product_id={product_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains the correct recommendation
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_id"], product_id)

    # ----------------------------------------------------------
    # TEST UPDATE - Successfully update a recommendation
    # ----------------------------------------------------------
    def test_update_recommendation(self):
        """It should Update an existing Recommendation"""
        # Create a recommendation
        test_recommendation = self._create_recommendations(1)[0]

        # New data for updating the recommendation
        new_data = {
            "product_id": test_recommendation.product_id + 1,  # Update product ID
            "recommended_id": test_recommendation.recommended_id
            + 1,  # Update recommended product ID
            "status": "expired",  # Update status
            "recommendation_type": "up-sell",  # Update recommendation type
            "like": test_recommendation.like + 1,  # Update number of likes
            "dislike": test_recommendation.dislike + 1,  # Update number of dislikes
        }

        # Send PUT request to update
        response = self.client.put(
            f"{BASE_URL}/{test_recommendation.id}", json=new_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Fetch the updated recommendation
        updated_recommendation = response.get_json()

        # Validate that the data has been updated
        self.assertEqual(updated_recommendation["product_id"], new_data["product_id"])
        self.assertEqual(
            updated_recommendation["recommended_id"], new_data["recommended_id"]
        )
        self.assertEqual(updated_recommendation["status"], new_data["status"])
        self.assertEqual(
            updated_recommendation["recommendation_type"],
            new_data["recommendation_type"],
        )
        self.assertEqual(updated_recommendation["like"], new_data["like"])
        self.assertEqual(updated_recommendation["dislike"], new_data["dislike"])

    # ----------------------------------------------------------
    # TEST UPDATE - Update a recommendation that does not exist
    # ----------------------------------------------------------
    def test_update_recommendation_not_found(self):
        """It should not Update a Recommendation that doesn't exist"""
        # Prepare new data for updating
        new_data = {
            "product_id": 1,
            "recommended_id": 101,
            "status": "expired",
            "recommendation_type": "up-sell",
            "like": 0,
            "dislike": 0,
        }

        # Use a non-existing ID for the PUT request
        response = self.client.put(f"{BASE_URL}/0", json=new_data)

        # Ensure the response is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE - Update with invalid data
    # ----------------------------------------------------------
    def test_update_recommendation_invalid_data(self):
        """It should not Update a Recommendation with invalid data"""
        # Create a recommendation
        test_recommendation = self._create_recommendations(1)[0]

        # Send data missing `recommended_id`
        invalid_data = {
            "product_id": test_recommendation.product_id + 1,
            "recommended_id": None,
            "status": "expired",
            "recommendation_type": "up-sell",
            "like": 0,
            "dislike": 0,
        }

        # Send PUT request with invalid data
        response = self.client.put(
            f"{BASE_URL}/{test_recommendation.id}", json=invalid_data
        )
        # Assert that the response should be 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()

        # Ensure the correct error message is returned
        self.assertIn("Invalid recommended_id", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE - invalid status
    # ----------------------------------------------------------
    def test_update_invalid_status(self):
        """It should not Update a Recommendation with an invalid status"""
        # Create a valid recommendation
        test_recommendation = self._create_recommendations(1)[0]

        # Prepare invalid data with all required fields
        invalid_data = {
            "product_id": test_recommendation.product_id,
            "recommended_id": test_recommendation.recommended_id,
            "recommendation_type": test_recommendation.recommendation_type,
            "status": "invalid-status",  # Invalid status value
            "like": 0,
            "dislike": 0,
        }

        # Send PUT request with invalid status
        response = self.client.put(
            f"{BASE_URL}/{test_recommendation.id}", json=invalid_data
        )

        # Assert that the response is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()

        # Assert that the error message contains 'Invalid status'
        self.assertIn("Invalid status", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE - invalid recommendation type
    # ----------------------------------------------------------
    def test_update_invalid_recommendation_type(self):
        """It should not Update a Recommendation with an invalid recommendation type"""
        # Create a valid recommendation
        test_recommendation = self._create_recommendations(1)[0]

        # Prepare invalid data with all required fields
        invalid_data = {
            "product_id": test_recommendation.product_id,
            "recommended_id": test_recommendation.recommended_id,
            "recommendation_type": "invalid-type",  # Invalid type value
            "status": test_recommendation.status,  # Include valid status
            "like": 0,
            "dislike": 0,
        }

        # Send PUT request with invalid recommendation_type
        response = self.client.put(
            f"{BASE_URL}/{test_recommendation.id}", json=invalid_data
        )

        # Assert that the response is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()

        # Assert that the error message contains 'Invalid recommendation_type'
        self.assertIn("Invalid recommendation_type", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE - Partial Update
    # ----------------------------------------------------------
    # def test_partial_update_recommendation(self):
    #     """It should Partially Update a Recommendation"""
    #     # Create a recommendation
    #     test_recommendation = self._create_recommendations(1)[0]

    #     # Only update the status
    #     partial_data = {"status": "expired"}

    #     # Send PUT request to partially update
    #     response = self.client.put(
    #         f"{BASE_URL}/{test_recommendation.id}", json=partial_data
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # Fetch the updated recommendation
    #     updated_recommendation = response.get_json()

    #     # Validate that the status has been updated
    #     self.assertEqual(updated_recommendation["status"], partial_data["status"])

    #     # Ensure other fields remain unchanged
    #     self.assertEqual(
    #         updated_recommendation["product_id"], test_recommendation.product_id
    #     )
    #     self.assertEqual(
    #         updated_recommendation["recommended_id"], test_recommendation.recommended_id
    #     )

    # ----------------------------------------------------------
    # TEST UPDATE - Boundary Conditions
    # ----------------------------------------------------------
    def test_update_with_boundary_values(self):
        """It should not Update a Recommendation with out-of-bound values"""
        # Create a recommendation
        test_recommendation = self._create_recommendations(1)[0]

        # Test with out-of-bound product_id (too small)
        invalid_data = {
            "product_id": 0,  # Invalid product ID (too small)
            "recommended_id": test_recommendation.recommended_id,
            "status": "active",
            "recommendation_type": "cross-sell",
            "like": 0,
            "dislike": 0,
        }

        # Send PUT request with invalid product_id
        response = self.client.put(
            f"{BASE_URL}/{test_recommendation.id}", json=invalid_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid product_id", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE - Invalid JSON Format
    # ----------------------------------------------------------
    def test_update_with_invalid_json(self):
        """It should not Update a Recommendation with malformed JSON"""
        test_recommendation = self._create_recommendations(1)[0]
        invalid_json = '{"product_id": 1, "recommended_id": 101, "status": "active", "recommendation_type": "cross-sell"'
        response = self.client.put(
            f"{BASE_URL}/{test_recommendation.id}",
            data=invalid_json,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid JSON format", data["message"])

    def test_update_recommendation_malformed_json(self):
        """It should return 400 Bad Request for malformed JSON in update"""
        test_recommendation = self._create_recommendations(1)[0]
        invalid_json = '{"product_id": 1, "recommended_id": 101, "status": "active"'  # Missing closing brace

        response = self.client.put(
            f"{BASE_URL}/{test_recommendation.id}",
            data=invalid_json,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid JSON format", data["message"])

    def test_check_content_type_invalid(self):
        """It should return 415 Unsupported Media Type when Content-Type is invalid"""
        test_recommendation = RecommendationsFactory()
        response = self.client.post(
            BASE_URL, data=test_recommendation.serialize(), content_type="text/plain"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    def test_update_recommendation_db_error(self):
        """It should return 500 Internal Server Error when a database error occurs during update"""
        # Create a recommendation to update
        test_recommendation = self._create_recommendations(1)[0]

        # Simulate a SQLAlchemyError during the update process
        with patch(
            "service.models.Recommendations.update",
            side_effect=SQLAlchemyError("Database error"),
        ):
            new_data = {
                "product_id": test_recommendation.product_id + 1,
                "recommended_id": test_recommendation.recommended_id + 1,
                "status": "expired",
                "recommendation_type": "up-sell",
                "like": 0,
                "dislike": 0,
            }
            response = self.client.put(
                f"{BASE_URL}/{test_recommendation.id}", json=new_data
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            # Check that the correct error message is returned
            data = response.get_json()
            self.assertIn("Internal server error", data["message"])

    def test_update_recommendation_unexpected_error(self):
        """It should return 500 Internal Server Error when an unexpected error occurs during update"""
        # Create a recommendation to update
        test_recommendation = self._create_recommendations(1)[0]

        # Simulate a generic Exception during the update process
        with patch(
            "service.models.Recommendations.update",
            side_effect=Exception("Unexpected error"),
        ):
            new_data = {
                "product_id": test_recommendation.product_id + 1,
                "recommended_id": test_recommendation.recommended_id + 1,
                "status": "expired",
                "recommendation_type": "up-sell",
                "like": 0,
                "dislike": 0,
            }
            response = self.client.put(
                f"{BASE_URL}/{test_recommendation.id}", json=new_data
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            # Check that the correct error message is returned
            data = response.get_json()
            self.assertIn("An unexpected error occurred", data["message"])

    # ----------------------------------------------------------
    # TEST ACTIONS - LIKE A RECOMMENDATION
    # ----------------------------------------------------------
    def test_like_a_recommendation(self):
        """It should Like a Recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        original_like = test_recommendation.like
        response = self.client.put(f"{BASE_URL}/{test_recommendation.id}/like")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["like"], original_like + 1)

    def test_like_a_nonexistent_recommendation(self):
        """It should return 404 error when a recommendation is not found"""
        # Use a non-existing ID for the PUT request
        response = self.client.put(f"{BASE_URL}/0/like")

        # Ensure the response is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])
