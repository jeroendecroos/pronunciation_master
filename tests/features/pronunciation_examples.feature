Feature: Get frequency list for language XXX
    We want to get a frequency list
    for a specific language

    Scenario: specific language
        Given I have the language "Dutch"
        When I ask for its frequency list
        Then I see the following at the top:
        """
        ik
        je
        het
        de
        dat
        """
