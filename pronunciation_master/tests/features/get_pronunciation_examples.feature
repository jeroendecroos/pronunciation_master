Feature: Get pronunciation examples for language XXX
    We want to get a dict {phoneme: word_list}
    for a specific language

    Scenario: specific language
        Given I have the language "Dutch"
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |


    Scenario: maximum words to try
        Given I have the language "Dutch"
        Given I want to try maximum "2" words
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |
            | k   | ik    |
        Then I don't see the following in the dict-list:
            | key | value |
            | v   | van   |

    Scenario: warning not enough minimum examples
        Given I have the language "Dutch"
        Given I want to get minimum "1" examples
        Given I want to try maximum "1" words
        When I ask for pronunciation examples
        Then I "do" see the warning message "Couldn't find enough examples (1) for 'j'"

    Scenario: minimum examples found for letter
        Given I have the language "Dutch"
        Given I want to get minimum "1" examples
        Given I want to try maximum "2" words
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |
            | j   | je    |
        Then I "don't" see the warning message "Couldn't find enough examples (1) for 'j'"

    Scenario: 1 maximum example
        Given I have the language "Dutch"
        Given I want to get maximum "1" examples
        Given I want to try maximum "6" words
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |
            | d   | de    |

    Scenario: 1000 maximum examples
        Given I have the language "Dutch"
        Given I want to get maximum "1000" examples
        Given I want to try maximum "6" words
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |
            | d   | de    |
            | d   | dat    |

    Scenario: Bad language
        Given I have the language "unknown"
        When I ask for pronunciation examples
        Then I see the error message "Language 'unknown' is not known"
