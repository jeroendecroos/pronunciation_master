Feature: Store the different data into a database
    data consist of phonemes, frequency lists, and pronunciation data
    for a specific language

    Scenario: store phonemes correct values
        Given I have the language "Dutch"
        Given I find no "phonemes" in mongodb
        When I ask to store its "phonemes"
        Then I find in mongodb:
            | value |
            | m     |
            | k     |

    Scenario: store phonemes count
        Given I have the language "Dutch"
        Given I find no "phonemes" in mongodb
        When I ask to store its "phonemes"
        Then I count "XX" entries in mongodb:

Feature: Give error message when using unknown language
    Scenario: Bad language
        Given I have the language "unknown"
        When I ask to store its <data>
        Then I see the error message "Language 'unknown' is not known"
    Examples:
        | data     |
        | phonemes |
        | frequent_words |
        | pronunciations |

