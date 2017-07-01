Feature: Get pronunciation examples for language XXX
    We want to get a dict {phoneme: word_list}
    for a specific language

    Scenario: specific language
        Given I have the language "Dutch"
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |


    Scenario: specific language
        Given I have the language "Dutch"
        Given I want to try maximum "1" words
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |
            | k   | ik    |
        Then I don't see the following in the dict-list:
            | key | value |
            | v   | van   |


    Scenario: Bad language
        Given I have the language "unknown"
        When I ask for pronunciation examples
        Then I see the error message "Language 'unknown' is not known"
