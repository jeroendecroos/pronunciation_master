Feature: Store the different data into a database
    data consist of phonemes, frequency lists, and pronunciation data

    Scenario: Create empty database
        Given there is not the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        Then I see the following tables in the database:
            """
            phonemes
            word_frequencies
            pronunciations
            """

    Scenario: do nothing when already database
        Given there is the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        Then I see the error message "database 'pronunciation_master_test' already exists"


    Scenario: Bad language
        Given I have the language "unknown"
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "<which_table>"
        Then I see the error message "Language 'unknown' is not known"
        Examples:
        | which_table      |
        | phonemes         |
        | word_frequencies |
        | pronunciations   |


    Scenario: Store phonemes
        Given I have the language "dutch"
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "phonemes"
        Then I find the following in the table "phonemes":
        | phonemes       |
        | m              |
        | k              |


    Scenario: Store pronunciations
        Given I have the language "dutch"
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "pronunciations"
        Then I find the following in the table "pronunciations":
        | word | ipa_orig | ipa_processed |
        | nu   | ny       | n,y           |
        | het  | ɦɛt      | ɦ,ɛ,t         |
        | het  | ət       | ə,t           |


    Scenario: Store frequencies
        Given I have the language "dutch"
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "word_frequencies"
        Then I find the following in the table "word_frequencies"
        | word | ranking  | occurances    |
        | ik   | 1        | 0             |
        | je   | 2        | 0             |
        | het  | 3        | 0             |
