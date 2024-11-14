Feature: The recommendations service back-end
    As a Sales Manager
    I need a RESTful catalog service
    So that I can keep track of all my recommendations

Background:
    Given the following recommendations
        | product_id | recommended_id | recommendation_type | status  | like | dislike |
        | 1          | 101            | cross-sell          | active  | 0    | 0       |
        | 2          | 102            | up-sell             | expired | 0    | 0       |
        | 3          | 103            | accessory           | draft   | 0    | 0       |
        | 4          | 104            | accessory           | active  | 0    | 0       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    When I enter "12345" in the "Product ID" field
    And I enter "67890" in the "Recommended ID" field
    And I set the "Recommendation Type" to "Accessory"
    And I set the "Status" to "Active"
    And I press the "Create" button
    Then I should see the message "Success"
    
    When I copy the "Recommendation ID" field
    And I press the "Clear" button
    Then the "Product ID" field should be empty
    And the "Recommended ID" field should be empty
    And the "Recommendation Type" field should be empty
    And the "Status" field should be empty
    
    When I paste the "Recommendation ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "12345" in the "Product ID" field
    And I should see "67890" in the "Recommended ID" field
    And I should see "Accessory" in the "Recommendation Type" field
    And I should see "Active" in the "Status" field


Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "101" in the results
    And I should see "102" in the results
    And I should not see "105" in the results

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