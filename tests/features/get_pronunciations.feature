Feature: Get frequency list for language XXX
    We want to get a frequency list
    for a specific language

    Scenario: specific language
        Given I have the language "Dutch"
        Given I have the word "nu"
        When I ask for its pronunciations
        Then I see the following in the list:
        """
        ny
        """

    Scenario: Bad language
        Given I have the language "unknown"
        Given I have the word "nu"
        When I ask for its pronunciations
        Then I see the error message "Language 'unknown' is not known"

    Scenario: no pronunciatons
        Given I have the language "Dutch"
        Given I have the word "blablaword"
        When I ask for its pronunciations
        Then I see the error message "No pronunciations found for word 'blablaword' in language 'Dutch'"

