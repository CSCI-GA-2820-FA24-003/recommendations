Feature: The recommendations service back-end
    As a Sales Manager
    I need a RESTful catalog service
    So that I can keep track of all my recommendations

Background:
    Given the following recommendations
        | product_id | recommended_id | recommendation_type | status  | like | dislike |
        | 1          | 101            | cross-sell          | active  | 2    | 0       |
        | 2          | 102            | up-sell             | expired | 0    | 1       |
        | 3          | 103            | accessory           | draft   | 1    | 1       |
        | 4          | 104            | accessory           | active  | 4    | 0       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations RESTful Service" in the title
    And I should not see "404 Not Found"

# Scenario: Create a Recommendation
#     When I visit the "Home Page"
#     And I set the "Name" to "Happy"
#     And I set the "Category" to "Hippo"
#     And I select "False" in the "Available" dropdown
#     And I select "Male" in the "Gender" dropdown
#     And I set the "Birthday" to "06-16-2022"
#     And I press the "Create" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Clear" button
#     Then the "Id" field should be empty
#     And the "Name" field should be empty
#     And the "Category" field should be empty
#     When I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see the message "Success"
#     And I should see "Happy" in the "Name" field
#     And I should see "Hippo" in the "Category" field
#     And I should see "False" in the "Available" dropdown
#     And I should see "Male" in the "Gender" dropdown
#     And I should see "2022-06-16" in the "Birthday" field

# Scenario: List all recommendations
#     When I visit the "Home Page"
#     And I press the "Search" button
#     Then I should see the message "Success"
    # And I should see "1" in the results
    # And I should see "103" in the results
    # And I should not see "5" in the results

# Scenario: Search for dogs
#     When I visit the "Home Page"
#     And I set the "Category" to "dog"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should not see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Search for available
#     When I visit the "Home Page"
#     And I select "True" in the "Available" dropdown
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should see "sammy" in the results
#     And I should not see "leo" in the results

# Scenario: Update a Recommendation
#     When I visit the "Home Page"
#     And I set the "Name" to "fido"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the "Name" field
#     And I should see "dog" in the "Category" field
#     When I change "Name" to "Loki"
#     And I press the "Update" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Clear" button
#     And I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see the message "Success"
#     And I should see "Loki" in the "Name" field
#     When I press the "Clear" button
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "Loki" in the results
#     And I should not see "fido" in the results

# Scenario: Delete a Recommendation
#     When I visit the "Home Page"
#     And I set the "Name" to "fido"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the "Name" field
#     And I should see "dog" in the "Category" field

#     When I copy the "Id" field
#     And I press the "Clear" button
#     And I paste the "Id" field
#     And I press the "Delete" button
#     Then I should see the message "Recommendation has been Deleted!"
#     When I press the "Clear" button
#     And I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see the message "404 Not Found"