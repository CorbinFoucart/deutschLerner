# startConsole.py
# Corbin Foucart

# description needed
# basically this is the launch console that
# allows the user to interact with the DL
# program

# import
import germanDatabase as db 
from nameConstants import *


def main():
    #database = dm.FlashcardDatabase('dictionary.csv')
    print "----------------------------------------------"
    print "WELCOME TO THE DeutschLerner DATABASE MANAGER"
    print "----------------------------------------------"
    
    gdb = db.questionDictionary(DICTIONARY_NAME)

    while True:
        printMenu()
        response = str(raw_input('Enter an action: '))
        if (response == QUIT_SENTINEL):
            break
        if (response == ADD_TO_DB):
            addNewEntry(gdb)
        if (response == READ_DICTIONARY):
            readDict(gdb)
        if (response == READ_GROUP):
            readGroup(gdb)
        if (response == SWITCH_GROUP):
            switchGroup(gdb)
        if (response == REMOVE_FROM_DB):
            removeEntry(gdb)
        if (response == EDIT_DB_ENTRY):
            editEntry(gdb)
        if (response == EDIT_LEITNER_BOX):
            editLeitnerBox(gdb)

def printMenu():
    print 
    print "Database Manager Menu: "
    print ADD_TO_DB.ljust(MENU_STR_LENGTH)       + "-- add new entries to the database"
    print READ_DICTIONARY.ljust(MENU_STR_LENGTH) + "-- read the current dictionary output"
    print READ_GROUP.ljust(MENU_STR_LENGTH)      + "-- read the current word group output"
    print SWITCH_GROUP.ljust(MENU_STR_LENGTH)    + "-- change current editing group"
    print REMOVE_FROM_DB.ljust(MENU_STR_LENGTH)  + "-- remove entry from group"
    print EDIT_DB_ENTRY.ljust(MENU_STR_LENGTH)   + "-- edit group entry" 
    print QUIT_SENTINEL.ljust(MENU_STR_LENGTH)   + "-- quit"
    print

def addNewEntry(db):
    while True:
        print 
        db.addEntryToDB()
        print
        cont = str(raw_input('Add another (y/n)?: ')).lower()
        if (cont != 'y' and cont != 'yes'):
            break

def readDict(db):
    db.printDictionary()

def readGroup(db):
    if (db.currentGroup == None):
        print
        print 'No editing group selected.'
        switchGroup(db)
    db.currentGroup.printGroup()

def switchGroup(db):
    gn = str(raw_input('Enter name of new editing group: '))
    db.changeCurrentGroup(gn)

def removeEntry(db):
    if (db.currentGroup == None):
        print
        print 'No editing group selected.'
        switchGroup(db)
    rmNum = int(raw_input('Enter the number of the question to remove: '))
    question = db.currentGroup.questions[rmNum - 1]
    db.removeEntryFromDB(question)

    # print it to show changes?
    db.currentGroup.printGroup()

def editEntry(db):
    if (db.currentGroup == None):
        print
        print 'No editing group selected.'
        switchGroup(db)
    print 
    db.currentGroup.printGroup()
    print 
    rmNum = int(raw_input('Enter the number of the question to edit: '))
    question = db.currentGroup.questions[rmNum - 1]
    db.editDBEntry(question)

    db.currentGroup.printGroup()

def editLeitnerBox(db):
    if (db.currentGroup == None):
        print
        print 'No editing group selected.'
        switchGroup(db)
    print 
    db.currentGroup.printGroup()
    print 

    qNum   = int(raw_input('Enter the number of the question to edit: '))
    newBox = int(raw_input('Enter the new Leitner Box: '))

    question = db.currentGroup.questions[qNum - 1]
    db.editDBLeitnerBox(question, newBox)
    db.currentGroup.printGroup()


# fire it up
if __name__ == '__main__':
	main()