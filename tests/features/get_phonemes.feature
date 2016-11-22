Feature: Get frequency list for language XXX
    We want to get a frequency list
    for a specific language

    Scenario: specific language
        Given I have the language "Dutch"
        When I ask for its phonemes
        Then I see the following at the top:
        """
        m
        k
        i
        j
        p
        """

    Scenario: Bad language
        Given I have the language "unknown"
        When I ask for its phonemes
        Then I see the error message "Language 'unknown' is not known"
