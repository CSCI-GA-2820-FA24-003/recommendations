"""
Models for Recommendations

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Recommendations(db.Model):
    """
    Class that represents a Recommendations
    """

    # pylint: disable=too-many-instance-attributes

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each recommendation
    _product_id = db.Column(
        "product_id", db.Integer, nullable=False
    )  # ID of the basic product
    _recommended_id = db.Column(
        "recommended_id", db.Integer, nullable=False
    )  # ID of the recommended product
    _recommendation_type = db.Column(
        "recommendation_type",
        db.Enum("cross-sell", "up-sell", "accessory", name="recommendation_type"),
        nullable=False,
    )  # Type of recommendation (cross-sell, up-sell, accessory)
    _status = db.Column(
        "status", db.Enum("active", "expired", "draft", name="status"), nullable=False
    )  # Status of the recommendation
    # Database auditing fields
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )
    like = db.Column(db.Integer, default=0, nullable=False)
    dislike = db.Column(db.Integer, default=0, nullable=False)

    @property
    def product_id(self):
        """This property provides access to the product id."""
        return self._product_id

    @product_id.setter
    def product_id(self, value):
        """This setter validates and updates the product id."""
        if not isinstance(value, int):
            raise DataValidationError("Invalid product_id: must be an integer")
        if value <= 0:
            raise DataValidationError("Invalid product_id: must be a positive number")
        self._product_id = value

    @property
    def recommended_id(self):
        """This property provides access to the recommended id."""
        return self._recommended_id

    @recommended_id.setter
    def recommended_id(self, value):
        """This setter validates and updates the recommended id."""
        if not isinstance(value, int):
            raise DataValidationError("Invalid recommended_id: must be an integer")
        if value <= 0:
            raise DataValidationError(
                "Invalid recommended_id: must be a positive number"
            )
        self._recommended_id = value

    @property
    def recommendation_type(self):
        """This property provides access to the recommendation type."""
        return self._recommendation_type

    @recommendation_type.setter
    def recommendation_type(self, value):
        """This setter validates and updates the recommendation type."""
        if value not in ["cross-sell", "up-sell", "accessory"]:
            raise DataValidationError(
                "Invalid recommendation_type: must be one of ['cross-sell', 'up-sell', 'accessory']"
            )
        self._recommendation_type = value

    @property
    def status(self):
        """This property provides access to the status."""
        return self._status

    @status.setter
    def status(self, value):
        """This setter validates and updates the status."""
        if value not in ["active", "expired", "draft"]:
            raise DataValidationError(
                "Invalid status: must be one of ['active', 'expired', 'draft']"
            )
        self._status = value

    def __repr__(self):
        return f"<Recommendation id=[{self.id}] product_id=[{self.product_id}] recommended_id=[{self.recommended_id}]>"

    def create(self):
        """
        Saves a Recommendation to the database
        """
        logger.info(
            "Creating recommendation: product_id=%s, recommended_id=%s",
            self.product_id,
            self.recommended_id,
        )
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(
                "Error creating recommendation: product_id=%s, recommended_id=%s. Error: %s",
                self.product_id,
                self.recommended_id,
                str(e),
            )
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Recommendation in the database, ensuring no concurrent modifications
        """
        logger.info(
            "Updating recommendation: product_id=%s, recommended_id=%s",
            self.product_id,
            self.recommended_id,
        )
        try:
            # Ensure the record hasn't been updated by another process
            current = Recommendations.find(self.id)
            if current and current.last_updated != self.last_updated:
                raise DataValidationError("The record was updated by another process.")

            db.session.commit()
        except DataValidationError as e:
            db.session.rollback()
            logger.error("Data validation error: %s", str(e))
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(
                "Error updating recommendation: product_id=%s, recommended_id=%s. Error: %s",
                self.product_id,
                self.recommended_id,
                str(e),
            )
            raise DataValidationError(e) from e

    def delete(self):
        """
        Removes a Recommendation from the database
        """
        logger.info(
            "Deleting recommendation: product_id=%s, recommended_id=%s",
            self.product_id,
            self.recommended_id,
        )
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(
                "Error deleting recommendation: product_id=%s, recommended_id=%s. Error: %s",
                self.product_id,
                self.recommended_id,
                str(e),
            )
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "recommended_id": self.recommended_id,
            "recommendation_type": self.recommendation_type,
            "status": self.status,
            "last_updated": self.last_updated,
            "created_at": self.created_at,
            "like": self.like,
            "dislike": self.dislike,
        }

    def deserialize(self, data):
        """Deserialize a Recommendation from a dictionary"""
        try:
            self.product_id = data["product_id"]
            self.recommended_id = data["recommended_id"]
            self.recommendation_type = data["recommendation_type"]
            self.status = data["status"]
        except AttributeError as error:
            raise DataValidationError(f"Invalid attribute: {error.args[0]}") from error
        except KeyError as error:
            raise DataValidationError(
                f"Invalid Recommendations: missing {error.args[0]}"
            ) from error
        except TypeError as error:
            raise DataValidationError(
                f"Invalid Recommendations: body of request contained bad or no data. {str(error)}"
            ) from error

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Recommendations in the database"""
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Recommendation by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_product_id(cls, product_id):
        """Returns all Recommendations with the given product_id

        Args:
            product_id (int): the ID of the product you want to match
        """
        logger.info("Processing product_id query for %s ...", product_id)
        return cls.query.filter(cls._product_id == product_id).all()

    @classmethod
    def find_by_recommended_id(cls, recommended_id):
        """Returns all Recommendations with the given recommended_id

        Args:
            recommended_id (int): the ID of the recommended product you want to match
        """
        logger.info("Processing recommended_id query for %s ...", recommended_id)
        return cls.query.filter(cls._recommended_id == recommended_id).all()

    @classmethod
    def find_by_filters(cls, filters):
        """
        Dynamically query Recommendations based on the provided filters

        Args:
            filters (dict): Dictionary of filters with the following possible keys:
                - product_id (int): ID of the target product
                - recommended_id (int): ID of the recommended product
                - recommendation_type (str): Type of recommendation
                - status (str): Status of the recommendation
                - created_at_min (datetime): Minimum creation date
                - created_at_max (datetime): Maximum creation date
                - page (int): Page number for pagination, default is 1
                - limit (int): Number of results per page, default is 10
                - sort_by (str): Field to sort by, default is "created_at"
                - order (str): Sort order, "asc" or "desc", default is "desc"
                - fields (list): List of fields to return, default is None for all fields

        Returns:
            list: List of Recommendations matching the filters
        """
        query = cls.query

        # Apply filters, date range, sorting, and pagination
        query = cls._apply_filters(query, filters)
        query = cls._apply_date_range(query, filters)
        query = cls._apply_sorting(query, filters)
        query = cls._apply_pagination(query, filters)

        return query.all()

    @classmethod
    def _apply_filters(cls, query, filters):
        """Apply multiple conditions based on filters"""
        if "product_id" in filters:
            query = query.filter(cls._product_id == filters["product_id"])
        if "recommended_id" in filters:
            query = query.filter(cls._recommended_id == filters["recommended_id"])
        if "recommendation_type" in filters:
            query = query.filter(
                cls._recommendation_type == filters["recommendation_type"]
            )
        if "status" in filters:
            query = query.filter(cls._status == filters["status"])
        return query

    @classmethod
    def _apply_date_range(cls, query, filters):
        """Apply date range filtering for created_at field"""
        if "created_at_min" in filters:
            query = query.filter(cls.created_at >= filters["created_at_min"])
        if "created_at_max" in filters:
            query = query.filter(cls.created_at <= filters["created_at_max"])
        return query

    @classmethod
    def _apply_sorting(cls, query, filters):
        """Apply sorting based on specified field and order"""
        sort_by = filters.get("sort_by", "created_at")
        order = filters.get("order", "desc")
        if sort_by in ["created_at", "product_id", "recommended_id", "last_updated"]:
            query = query.order_by(
                getattr(cls, sort_by).asc()
                if order == "asc"
                else getattr(cls, sort_by).desc()
            )
        return query

    @classmethod
    def _apply_pagination(cls, query, filters):
        """Apply pagination based on page and limit"""
        page = filters.get("page", 1)
        limit = filters.get("limit", 10)
        offset = (page - 1) * limit
        return query.offset(offset).limit(limit)
