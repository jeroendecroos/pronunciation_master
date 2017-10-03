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

    @now
    Scenario: use stored data
        Given there is not the database 'pronunciation_master_test'
        Given I ask to create an empty database "pronunciation_master_test"
        Given I have the language "dutch"
        Given there is the following in the table "phonemes":
        | ipa            |
        | k              |
        | i              |
        | m              |
        Given there is the following in the table "word_frequencies":
        | word | int:ranking | int:occurances |
        | ik   | 1           | 8106228        |
        | me   | 2           | 7305984        |
        | mik  | 3           | 5706767        |
        Given there is the following in the table "pronunciations":
        | word | original_pronunciation | ipa_pronunciation |
        | ik   | ik                     | i,k               |
        | me   | mi                     | m,i               |
        | mik  | mik                    | m,i,k             |
        Given I want to get the data from the database "only":
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |
            | i   | ik    |
            | k   | mik   |
            | m   | me    |

    Scenario: use stored data if possible
        Given there is not the database 'pronunciation_master_test'
        Given I ask to create an empty database "pronunciation_master_test"
        Given I have the language "dutch"
        Given there is the following in the table "word_frequencies":
        | word | int:ranking | int:occurances |
        | ik   | 1           | 8106228        |
        | me   | 2           | 7305984        |
        | mik  | 3           | 5706767        |
        Given there is the following in the table "pronunciations":
        | word | original_pronunciation | ipa_pronunciation |
        | ik   | mik                    | m,i,k               |
        Given I want to get the data from the database "if_possible"
        When I ask for pronunciation examples
        Then I see the following in the dict-list:
            | key | value |
            | i   | ik    |
            | k   | mik   |
            | m   | ik    |

