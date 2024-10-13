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
Recommendations Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendations
"""

from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest
from service.models import Recommendations
from service.common import status  # HTTP Status Codes
from service.models import DataValidationError


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the recommendations"""
    app.logger.info("Request for recommendation list")

    recommendations = []

    # Parse any arguments from the query string
    product_id = request.args.get("product_id")
    recommended_id = request.args.get("recommended_id")

    if product_id:
        app.logger.info("Find by product_id: %s", product_id)
        # Validate product_id is an integer
        try:
            product_id = int(product_id)
            recommendations = Recommendations.find_by_product_id(product_id)
        except ValueError:
            app.logger.error("Invalid product_id")
            raise BadRequest("Invalid product_id: must be an integer")
    elif recommended_id:
        app.logger.info("Find by recommended_id: %s", recommended_id)
        # Validate recommended_id is an integer
        try:
            recommended_id = int(recommended_id)
            recommendations = Recommendations.find_by_recommended_id(recommended_id)
        except ValueError:
            app.logger.error("Invalid recommended_id")
            raise BadRequest("Invalid recommended_id: must be an integer")
    else:
        app.logger.info("Find all")
        recommendations = Recommendations.all()

    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# CREATE A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Create a Recommendation
    This endpoint will create a Recommendation based the data in the body that is posted
    """
    app.logger.info("Request to Create a Recommendation...")
    check_content_type("application/json")

    try:
        recommendation = Recommendations()
        # Get the data from the request and deserialize it
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        recommendation.deserialize(data)

        # Save the new Recommendation to the database
        recommendation.create()
    except DataValidationError as e:
        app.logger.error("Data validation error: %s", str(e))
        abort(status.HTTP_400_BAD_REQUEST, str(e))
    except SQLAlchemyError as e:
        app.logger.error("Database error: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error occurred")
    except Exception as e:
        app.logger.error("Unexpected error: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred")

    app.logger.info("Recommendation with new id [%s] saved!", recommendation.id)

    # Todo: uncomment this code when get_recommendations is implemented
    # Return the location of the new Recommendation
    # location_url = url_for(
    #     "get_recommendations", recommendation_id=recommendation.id, _external=True
    # )
    location_url = "/"
    return (
        jsonify(recommendation.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# READ A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendations(recommendation_id):
    """
    Retrieve a single Recommendation

    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info(
        "Request to Retrieve a recommendation with id [%s]", recommendation_id
    )

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendations.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    app.logger.info("Returning recommendation: %s", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendations(recommendation_id):
    """
    Delete a Recommendation
    This endpoint will delete a Recommendation based the id specified in the path
    """
    app.logger.info(
        "Request to Delete a recommendation with id [%s]", recommendation_id
    )

    # Find the recommendation by id
    recommendation = Recommendations.find(recommendation_id)

    if recommendation:
        app.logger.info(
            "Recommendation with ID: %d found. Deleting...", recommendation_id
        )
        try:
            recommendation.delete()
        except SQLAlchemyError as e:
            app.logger.error("Database error while deleting: %s", str(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error occurred")
        except Exception as e:
            app.logger.error("Unexpected error: %s", str(e))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred")
    else:
        app.logger.info(
            "Recommendation with ID: %d not found. Returning 204 No Content.",
            recommendation_id,
        )

    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendations(recommendation_id):
    """
    Update a Recommendation

    This endpoint will update a Recommendation based on the posted data
    """
    app.logger.info(
        "Request to Update a recommendation with id [%s]", recommendation_id
    )
    check_content_type("application/json")

    # Find the recommendation by id
    recommendation = Recommendations.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # Get the data from the request and handle malformed JSON
    try:
        data = request.get_json()
    except BadRequest as e:
        app.logger.error("Invalid JSON format: %s", str(e))
        abort(status.HTTP_400_BAD_REQUEST, "Invalid JSON format")

    app.logger.info("Processing update for recommendation: %s", data)

    try:
        # Deserialize and update the recommendation
        recommendation.deserialize(data)
        recommendation.update()
    except DataValidationError as e:
        # Handle concurrent modification or other validation errors
        app.logger.error("Data validation error: %s", str(e))
        if "updated by another process" in str(e):
            abort(
                status.HTTP_409_CONFLICT, "The record was updated by another process."
            )
        abort(status.HTTP_400_BAD_REQUEST, str(e))
    except SQLAlchemyError as e:
        app.logger.error("Database error: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
    except Exception as e:
        app.logger.error("Unexpected error: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred")

    app.logger.info("Recommendation with id [%s] updated!", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
