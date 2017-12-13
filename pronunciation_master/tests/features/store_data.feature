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
            pronunciation_examples
            """

    Scenario: do nothing when already database
        Given there is the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        Then I see the approximate error message "database '.*pronunciation_master_test' already exists"


    Scenario: Bad language
        Given I have the language "unknown"
        Given there is not the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "<which_table>"
        Then I see the error message "Language 'unknown' is not known"
        Examples:
        | which_table      |
        | phonemes         |
        | word_frequencies |
        | pronunciations   |
        | pronunciation_examples   |


    Scenario: Store phonemes
        Given I have the language "dutch"
        Given there is not the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "phonemes"
        Then I find the following in the table "phonemes":
        | ipa            |
        | m              |
        | k              |


    @new
    Scenario: Store only once
        Given I have the language "dutch"
        Given there is not the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "phonemes"
        When I ask to store the "phonemes"
        Then I find no duplicates in the table "phonemes" for the following columns
            """
            ipa
            language
            """

    Scenario: Store pronunciations
        Given I have the language "dutch"
        Given there is not the database 'pronunciation_master_test'
	Given I have an empty mongodb
	Given I have a mongodb with per language and per word
	| key       | value    |
        | niet      | nit      |
        | het       | ɦɛt,ət   |
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "pronunciations"
        Then I find the following in the table "pronunciations":
        | word | original_pronunciation | ipa_pronunciation |
        | niet | nit                    | n,i,t             |
        | het  | ɦɛt                    | ɦ,ɛ,t             |
        | het  | ət                     | ə,t               |


    Scenario: Store with specifications of datagetter
        Given I have the language "dutch"
        Given there is not the database 'pronunciation_master_test'
	Given I have an empty mongodb
	Given I have a mongodb with per language and per word
	| key       | value    |
        | niet      | nit      |
        | het       | ɦɛt,ət   |
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "pronunciations" with "max_words=5"
        Then I find the following in the table "pronunciations":
        | word | original_pronunciation | ipa_pronunciation |
        | het  | ɦɛt                    | ɦ,ɛ,t             |
        | het  | ət                     | ə,t               |
        Then I "do not" find the following in the table "pronunciations":
        | word | original_pronunciation | ipa_pronunciation |
        | niet | nit                    | n,i,t             |


    Scenario: Specifications for datagetter not valid
        Given I have the language "dutch"
        Given there is not the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "phonemes" with "max_words=5"
        Then I see the approximate error message "error: unrecognized arguments: --max_words 5"


    Scenario: Store frequencies
        Given I have the language "dutch"
        Given there is not the database 'pronunciation_master_test'
        When I ask to create an empty database "pronunciation_master_test"
        When I ask to store the "word_frequencies"
        Then I find the following in the table "word_frequencies"
        | word | int:ranking | int:occurances |
        | ik   | 1           | 8106228        |
        | je   | 2           | 7305984        |
        | het  | 3           | 5706767        |

    Scenario: Store pronunciation_examples
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
        | mik  | 2           | 7305984        |
        | me   | 3           | 5706767        |
        Given there is the following in the table "pronunciations":
        | word | original_pronunciation | ipa_pronunciation |
        | ik   | ik                     | i,k               |
        | me   | mi                     | m,i               |
        | mik  | mik                    | m,i,k             |
        When I ask to store the "pronunciation_examples"
        Then I find the following in the table "pronunciation_examples"
        | ipa     | examples            |
        | i       | ['ik', 'mik', 'me'] |
        | k       | ['ik', 'mik']       |
        | m       | ['mik', 'me']       |
