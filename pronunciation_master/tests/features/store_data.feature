Feature: Store the different data into a database
    data consist of phonemes, frequency lists, and pronunciation data

    Scenario: Create empty database
        Given there is not the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        Then I see the following tables in the database:
            """
            phonemes
            frequency_lists
            pronunciations
            """

    Scenario: do nothing when already database
        Given there is the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        Then I see the error message "database 'pronunciation_master_test' already exists"


#    for a specific language
#    Scenario: Bad language
#        Given I have the language "unknown"
#        When I ask to store its <data>
#        Then I see the error message "Language 'unknown' is not known"
#    Examples:
#        | data     |
#        | phonemes |
#        | frequent_words |
#        | pronunciations |

