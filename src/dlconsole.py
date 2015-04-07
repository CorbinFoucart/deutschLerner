# merging of database console and the DL program

import databaseConsole as gDB
import quizManager as qm

def main():
    print("\033c")
    print "-------------------------------------"
    print "WELCOME TO THE DeutschLerner CONSOLE"
    print "-------------------------------------"

    while True:
        printMenu()
        userResponse = str(raw_input('Enter an option: ')).lower()
        if (userResponse == 'db'):
            gDB.main()
        elif (userResponse == 'qz'):
            qm.main()
        elif (userResponse == 'x'):
            printGoodbye()
            break
        else:
            invalidChoice()

def printMenu():
    print
    print "Main Menu: "
    print "db    -- access csv database menu"
    print "qz    -- access quiz taking menu"
    print "x  -- exit DeutschLerner"
    print

def printGoodbye():
    print
    print "Aufwiedersehen!"
    print

def invalidChoice():
    print
    print "Please enter a valid choice."
    print    

if __name__ == '__main__':
    main()
