# Global naming constants to ensure consistency in identifying type
# check is made during input to ensure that these are correct.

ACCEPTEDS_FILENAME = 'accepted_ids.csv'

# Question ID types
NOUN_ID          = 'N'
REG_VERB_ID      = 'RV'
IRREG_VERB_ID    = 'IV'
ADJECTIVE_ID     = 'A'
PREP_ID          = 'PR'
PHRASE_ID        = 'PH'
VERB_PREP_ID     = 'VPC'

## Menu Constant Strings
MENU_STR_LENGTH  = 6            # padded length of option strings

# database menu
QUIT_SENTINEL    = "qx"         # saves progress and quits program
ADD_TO_DB        = "add"        # adds new content to database 
READ_DICTIONARY  = "read"       # print entire dictionary
READ_GROUP       = "rg"         # print current editing group
SWITCH_GROUP     = "cg"         # change editing group 
REMOVE_FROM_DB   = "rm"         # remove item from database
EDIT_DB_ENTRY    = "edit"       # edit a database item
EDIT_LEITNER_BOX = "ELB"        # SECRETS SECRETS SECRETS

# quiz menu
BASIC_QUIZ       = "bq"
LEARNING_QUIZ    = "lq"
PRUNING_QUIZ     = "pq"

# German Database file operations
DICTIONARY_NAME = 'dictionary.csv'
TEMPORARY_DICT  = 'correction.csv'

ID_LENGTH = 5
PRINT_Q_GROUP = 0
PRINT_Q_DICT  = 1

# Quizzing constants
QUIZ_PENALTY = 3
PHASING_AREA_SIZE = 4

# Leitner Constants
LEITNER_NOT_ASKED    = -1
LEITNER_STAGING_AREA = 0
MAX_LEITNER_BOX      = 7
FIRST_LEITNER_BOX    = 1
STAGING_AREA_SIZE    = 10


