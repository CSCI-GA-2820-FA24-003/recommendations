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

from flask import jsonify, request, abort, url_for
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
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendation REST API Service",
            version="1.0",
            paths=url_for("list_recommendations", _external=True),
        ),
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
    # Utilize the general function find_by_filters
    # Thus first parse the passed-in filters
    filters = filters_from_args()
    recommendations = Recommendations.find_by_filters(filters)
    serialized_results = [
        recommendation.serialize() for recommendation in recommendations
    ]
    app.logger.info("Returning %d recommendations", len(serialized_results))
    return jsonify(serialized_results), status.HTTP_200_OK


######################################################################
# HELPER FUNCTIONS FOR LIST ROUTE
######################################################################
def parse_int_param(param_name):
    """Helper function to parse integer query parameters"""
    try:
        return int(request.args.get(param_name))
    except (ValueError, TypeError) as exc:
        app.logger.error("Invalid %s", param_name)
        raise BadRequest("Invalid data type: must be an integer") from exc


def validate_enum_param(param_name, value, valid_options):
    """Helper function to validate enum query parameters"""
    if value not in valid_options:
        app.logger.error("Invalid %s", param_name)
        raise BadRequest(f"Invalid {param_name}: must be one of {valid_options}")
    return value


def filters_from_args():
    """Helper function to build filters dictionary from query args"""
    filters = {}
    if "product_id" in request.args:
        filters["product_id"] = parse_int_param("product_id")
    if "recommended_id" in request.args:
        filters["recommended_id"] = parse_int_param("recommended_id")
    if "page" in request.args:
        filters["page"] = parse_int_param("page")
    if "limit" in request.args:
        filters["limit"] = parse_int_param("limit")
    if "recommendation_type" in request.args:
        filters["recommendation_type"] = validate_enum_param(
            "recommendation_type",
            request.args.get("recommendation_type"),
            ["cross-sell", "up-sell", "accessory"],
        )
    if "status" in request.args:
        filters["status"] = validate_enum_param(
            "status",
            request.args.get("status"),
            ["active", "expired", "draft"],
        )
    if "sort_by" in request.args:
        filters["sort_by"] = request.args.get("sort_by")
    if "order" in request.args:
        filters["order"] = request.args.get("order")
    return filters


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
    except Exception as e:  # pylint: disable=broad-except
        app.logger.error("Unexpected error: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred")

    app.logger.info("Recommendation with new id [%s] saved!", recommendation.id)

    # Return the location of the new Recommendation
    location_url = url_for(
        "get_recommendations", recommendation_id=recommendation.id, _external=True
    )
    # location_url = "/"
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
        except Exception as e:  # pylint: disable=broad-except
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
    except Exception as e:  # pylint: disable=broad-except
        app.logger.error("Unexpected error: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred")

    app.logger.info("Recommendation with id [%s] updated!", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# LIKE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/like", methods=["PUT"])
def like_recommendations(recommendation_id):
    """Liking a recommendation adds 1 to like"""
    app.logger.info("Request to like a recommendation with id: %d", recommendation_id)

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendations.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # At this point you would execute code to like the recommendation
    # For the moment, we will add the like by 1

    recommendation.like += 1
    recommendation.update()

    app.logger.info("Recommendation with ID: %d has been liked.", recommendation_id)
    return recommendation.serialize(), status.HTTP_200_OK


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
