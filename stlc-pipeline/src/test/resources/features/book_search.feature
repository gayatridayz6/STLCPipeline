@EPMCDMETST-66524
Feature: Book Store Search

  @AC1
  Scenario: Search for an existing book
    Given the user is on the book store homepage
    When the user searches for "Java Programming"
    Then the book details for "Java Programming" are displayed

  @AC2
  Scenario: Search for a non-existent book
    Given the user is on the book store homepage
    When the user searches for "Unknown Book XYZ"
    Then the message "No books found" is displayed
