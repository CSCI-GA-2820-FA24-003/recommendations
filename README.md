# Recommendations Microservice

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI Build](https://github.com/CSCI-GA-2820-FA24-003/recommendations/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/CSCI-GA-2820-FA24-003/recommendations/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/CSCI-GA-2820-FA24-003/recommendations/graph/badge.svg?token=JMMX72MSRI)](https://codecov.io/github/CSCI-GA-2820-FA24-003/recommendations)

## Overview

This project is about the recommendations service from an eCommerce website. The recommendations service is a representation a product recommendation based on another product. The `/service` folder contains the `models.py` file for the model and a `routes.py` file for the service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add the functionality.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## Base URL

`/recommendations`

## Database Model

The `Recommendations` table schema contains the following fields:

| Field             | Type                                      | Description                                                  |
|-------------------|-------------------------------------------|--------------------------------------------------------------|
| `id`              | `Integer`                                 | Unique ID for each recommendation (Primary Key)               |
| `product_id`      | `Integer`                                 | ID of the product                                             |
| `recommended_id`  | `Integer`                                 | ID of the recommended product                                 |
| `recommendation_type` | `Enum` ("cross-sell", "up-sell", "accessory") | Type of recommendation: cross-sell, up-sell, or accessory     |
| `status`          | `Enum` ("active", "expired", "draft")     | Status of the recommendation                                  |
| `created_at`      | `DateTime`                                | Timestamp when the recommendation was created                 |
| `last_updated`    | `DateTime`                                | Timestamp when the recommendation was last updated            |

## API Endpoints

| Method | Endpoint                                    | Description                              | Parameters                                  | Example Response                                                 |
|--------|---------------------------------------------|------------------------------------------|--------------------------------------------|------------------------------------------------------------------|
| GET    | `/recommendations`                          | List all recommendations                 | `product_id` (optional), `recommended_id` (optional) | `[ { "id": 1, "product_id": 101, "recommended_id": 202, "recommendation_type": "cross-sell", "status": "active" }, ... ]` |
| POST   | `/recommendations`                          | Create a new recommendation              | JSON body with `product_id`, `recommended_id`, `recommendation_type`, `status` | `{ "id": 1, "product_id": 101, "recommended_id": 202, "recommendation_type": "cross-sell", "status": "active" }`          |
| GET    | `/recommendations/<int:recommendation_id>`  | Retrieve a single recommendation by ID   | `recommendation_id` (required)             | `{ "id": 1, "product_id": 101, "recommended_id": 202, "recommendation_type": "cross-sell", "status": "active" }`          |
| PUT    | `/recommendations/<int:recommendation_id>`  | Update an existing recommendation by ID  | `recommendation_id` (required), JSON body with updated fields | `{ "id": 1, "product_id": 101, "recommended_id": 303, "recommendation_type": "up-sell", "status": "expired" }`          |
| DELETE | `/recommendations/<int:recommendation_id>`  | Delete a recommendation by ID            | `recommendation_id` (required)             | `{}` (empty response, status code 204)                           |

## Data Model Example

A `Recommendations` object is represented as follows:

```json
{
  "id": 1,
  "product_id": 101,
  "recommended_id": 202,
  "recommendation_type": "cross-sell",
  "status": "active",
  "created_at": "2024-10-13T12:00:00Z",
  "last_updated": "2024-10-13T15:00:00Z"
}
```

## Tests

The current unit test code coverage is `97%%` (last updated 12/04/2024). To test the microservice, run `make test`.

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
