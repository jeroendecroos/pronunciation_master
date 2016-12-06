Feature: Get pronunciation examples for language XXX
    We want to get a dict {phoneme: word_list}
    for a specific language

    Scenario: specific language
        Given I have the language "Dutch"
        When I ask for its pronunciation examples
        Then I see the following in the list:
        """
        y: [nu]
        """

    Scenario: Bad language
        Given I have the language "unknown"
        When I ask for its pronunciation examples
        Then I see the error message "Language 'unknown' is not known"
