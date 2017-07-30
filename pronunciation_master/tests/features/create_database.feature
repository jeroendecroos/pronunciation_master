Feature: Create a database according to specs

    Scenario: Create empty database
        Given There is not the database "pronunciation_master_test"
        When I ask to create an empty database "pronunciation_master_test"
        Then I find the database "pronunciation_master_test":

    Scenario: do nothing when already database
        Given There is the database "pronunciation_master_test"
        When I ask to create an empty database "pronunciation_master_test"
        Then I see the error message "database 'pronunciation_master_test' already exists"


#Feature: Store the different data into a database
#    data consist of phonemes, frequency lists, and pronunciation data
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

