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
        When I ask for its phonemes
        Then I see the error message "Language 'unknown' is not known"
