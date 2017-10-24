Feature: Process an offline wiktionary in xml format to a database

    Scenario: Extract raw pages
        Given I have an empty mongodb
        Given I have the wiktionary with entry:
            """
            <title>something</title>
            <text>hey</text>
            """
        When I ask for to process into mongodb
        When I ask to find in the mongodb
            | key | value |
            | title | something |
        Then I see the following in the mongodb:
            | key | value |
            | text | hey |



    Scenario: from raw to per raw_per_language
        Given I have an empty mongodb
        Given I have a mongodb with raw input
            | key | value |
            | title | leven |
            | text | {"text": '{{also\|l\xe9v\xe9n\|l\u0119ven\|Leven}}\n==English==\n\n===Etymology 1===\n\n====Noun====\n===Etymology 2===\n====Verb====\n==Dutch==\n\n===Pronunciation===\n* {{IPA\|/\u02c8le\u02d0v\u0259(n)/\|lang=nl}}\n* {{rhymes\|e\u02d0v\u0259n\|lang=nl}}\n* {{audio\|Nl-leven.ogg\|audio\|lang=nl}}\n\n===Etymology 1===\n====Verb====\n=====Inflection=====\n=====Derived terms=====\n*=====Descendants=====\n*===Etymology 2===\n====Noun====\n=====Derived terms=====\n*===Anagrams===dood\n*==Middle Dutch==\n\n===Etymology===\n===Verb===\n====Inflection====\n====Descendants====\n===Further reading===\n*==MiddleLow German==\n\n===Etymology===\n===Pronunciation===\n* \'\'\'[[Wiktionary:About_Middle_Low_German#Stem_vowels\|Stem vowel]]: \u0113\xb2\'\'\'\n** {{a\|originally}} {{IPA\|/l\u026a\u025bv\u0259n/\|lang=gml}}\n\n===Verb===\n====Conjugation====\n====Related terms====\n*====Descendants====\n*==Scots==\n\n===Noun===\n==Swedish==\n\n===Noun===\n===References===\n, u'title': u'leven'} |
        When I ask to process into language and category
        When I ask to find in the mongodb
            | key | value |
            | language | Dutch |
            | word     | leven |
            | section  | Pronunciation |


        Then I see the following in the mongodb json:
            | key      | value |
            | content |  \n* {{IPA\|/\u02c8le\u02d0v\u0259(n)/\|lang=nl}}\n* {{rhymes\|e\u02d0v\u0259n\|lang=nl}}\n* {{audio\|Nl-leven.ogg\|audio\|lang=nl}}\n\n |


    Scenario: raw_per_language to pronunciation per language
        Given I have an empty mongodb
        Given I have a mongodb with raw input per language
            | key | value |
            | language | Dutch |
            | word     | leven |
            | section  | Pronunciation |
            | content |  \n* {{IPA\|/\u02c8le\u02d0v\u0259(n)/\|lang=nl}}\n* {{rhymes\|e\u02d0v\u0259n\|lang=nl}}\n* {{audio\|Nl-leven.ogg\|audio\|lang=nl}}\n\n |
        When I ask to process into pronunciation per language
        When I ask to find in the mongodb
            | key | value |
            | language | Dutch |
            | word     | leven |
        Then I see the following in the mongodb json:
            | key | value                    |
            | IPA | ["\u02c8le\u02d0v\u0259(n)"] |
