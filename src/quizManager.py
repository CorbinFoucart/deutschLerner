# This file provides the console interaction of allowing the user
# to configure and take a quiz.
# Corbin Foucart

import germanDatabase as db
from nameConstants import *
import math
import datetime as dt
import os
import random
import csv

def main():
    print("\033c")
    database = db.questionDictionary(DICTIONARY_NAME)
    print "-------------------------------------------------"
    print "* WELCOME TO THE DeutschLerner QUIZ APPLICATION *"
    print "-------------------------------------------------"

    while True:
        printMenu()
        response = str(raw_input('Enter an action: ')).lower()
        if (response == QUIT_SENTINEL):
            break
        if (response == BASIC_QUIZ):
            questions = getQuestionsList(database)
            takeBasicQuiz(questions)
        if (response == LEARNING_QUIZ):
            questions = getQuestionsList(database)
            takeLearningQuiz(questions)
        if (response == PRUNING_QUIZ):
            pruningMode(database)


def printMenu():
    print
    print "Quiz Menu: "
    print BASIC_QUIZ     + "-- basic group quiz"
    print LEARNING_QUIZ  + "-- learning mode group quiz"
    print PRUNING_QUIZ   + "-- pruning mode quiz"
    print QUIT_SENTINEL  + "-- quit"

def getQuestionsList(database):
    groupName = str(raw_input("Specify a group name: "))
    group = database.loadGroupFromDictionary(groupName)
    questions = group.questions
    return questions

# the user takes a basic group quiz
def takeBasicQuiz(questionsFromFile):
    # load questions into a list
    questions = []
    for question in questionsFromFile:
        questions.append(question)

    # continue the quiz until the question list is empty
    while(len(questions) != 0):
        print 
        currQuestion = random.choice(questions)
        print currQuestion.question
        userAnswer = currQuestion.promptForUserAnswer()

        if (userAnswer.lower() == currQuestion.answer.lower()):
            questions.remove(currQuestion)
        else:
            print "Wrong!"
            print currQuestion.answer
            for i in range(QUIZ_PENALTY):
                questions.append(currQuestion)        

    printEndQuiz()

# the user takes a quiz in learning mode 
# questions filter through a phasing area, then through a final review
def takeLearningQuiz(questionsFromFile):
    questionPool = []
    for question in questionsFromFile:
        questionPool.append(question)
    phasingArea = [] 
    finalReview = []

    # phasing area filtering
    while(   len(questionPool) != 0 
          or len(phasingArea)  != 0):

        # move question from QP to PA, FR
        while (len(questionPool) > 0 
            and len(set(phasingArea)) < PHASING_AREA_SIZE):
            moveQuestion = random.choice(questionPool)
            questionPool.remove(moveQuestion)

            finalReview.append(moveQuestion)
            phasingArea.append(moveQuestion)

        currQuestion = random.choice(phasingArea)
        print currQuestion.question
        userAnswer = currQuestion.promptForUserAnswer()

        if (userAnswer.lower() == currQuestion.answer.lower()):
            phasingArea.remove(currQuestion)
        else:
            print "Wrong!"
            print currQuestion.answer
            for i in range(QUIZ_PENALTY):
                phasingArea.append(currQuestion)        

    # once phasing area questioning is over, 
    # go through a final review quiz
    takeBasicQuiz(finalReview)

# pruning mode quiz
def pruningMode(database):

    # select how much of time you want to be review
    while True:
        reviewPercentage = float(raw_input('Enter the percentage you would like to review: '))
        if (reviewPercentage < 0 or reviewPercentage > 1):
            print 
            print "A percentage is a number on [0,1]. Try again."
            reviewPercentage = float(raw_input('Enter the percentage you would like to review: '))
        else: 
            break
    print type(reviewPercentage)

    # load leitner boxes and stuff into memory
    print 
    print "loading question data..."
    print 

    leitnerArrays  = database.getLeitnerBoxArray()
    leitnerBoxes   = leitnerArrays[0]
    stagingArea    = leitnerArrays[1]
    leitnerUnasked = leitnerArrays[2]

    # initialize box probabilities
    boxProbabilities = []
    for i in range(MAX_LEITNER_BOX):
        print i
        boxProbabilities.append(1.0/2**(i+1))
    cumProbs = list(cumsum(boxProbabilities))

    print 'length: ', len(cumProbs)

    # all empty boxes check
    if (AllBoxesEmpty(leitnerBoxes)):
        print
        print "all Leitner Boxes empty. \
               switching to adding mode"
        print 
        reviewPercentage = 0
    
    # begin the quiz
    while True:
        # pruning mode
        if (questionReview(reviewPercentage)):
            
            # choose a leitner box that contains questions
            while True:

                boxNum = chooseLeitnerBox(cumProbs)
                if not (leitnerBoxes[boxNum - 1].isEmpty()):
                    break

            # never fly blind
            print 
            for q in leitnerUnasked:
                print q.getQuestionString()
            print 

            for box in leitnerBoxes:
                box.printBox()

            print 
            print 'Staging area:'
            for q in stagingArea:
                print q.getQuestionString()


            # choose a random question
            box = leitnerBoxes[boxNum - 1]
            cQuestion = random.choice(box.boxQuestions)

            # ask the question
            print
            print cQuestion.question
            userAnswer = cQuestion.promptForUserAnswer()

            # determine correctness, move the question
            if (userAnswer.lower() == cQuestion.answer.lower()):
                moveLeitnerBoxUp(cQuestion, database, leitnerBoxes)
            else:
                moveLeitnerBoxDown(cQuestion, database, leitnerBoxes)

        # adding mode    
        else:
            # no questions in staging area and unasked
            if ((not stagingArea) and (not leitnerUnasked)):
                print 
                print "no more unasked questions, changing review percentage to 1."
                reviewPercentage = 1
                print 
            else:
                # move questions as necessary to staging area
                nSAQuestions = len(stagingArea)
                while (len(stagingArea) < STAGING_AREA_SIZE
                       and leitnerUnasked):
                    moveFromUnaskedToSA(leitnerUnasked, stagingArea, database)

                # ask a question in the staging area
                cQuestion = random.choice(stagingArea)
                print
                print cQuestion.question
                userAnswer = cQuestion.promptForUserAnswer()

                # if right, move it to box 1 
                if (userAnswer.lower() == cQuestion.answer.lower()):
                    # change in csv
                    database.editDBLeitnerBox(cQuestion, FIRST_LEITNER_BOX, 1)

                    # change locally
                    stagingArea.remove(cQuestion)
                    cQuestion.box = FIRST_LEITNER_BOX
                    leitnerBoxes[FIRST_LEITNER_BOX - 1].addQuestion(cQuestion)




            

def moveFromUnaskedToSA(unasked, SA, db):
    q = random.choice(unasked)

    # change locally
    unasked.remove(q)
    newBox = LEITNER_STAGING_AREA
    q.box  = newBox
    SA.append(q)

    # change in csv
    db.editDBLeitnerBox(q, newBox, 1)

def questionReview(reviewPercentage):
    return random.random() < reviewPercentage

def cumsum(probList):
    total = 0
    for x in probList:
        total += x
        yield total

def chooseLeitnerBox(cProbs):
    rDec = random.random()
    idx = next((cProbs.index(n) for n in cProbs if n > rDec), len(cProbs))
    boxNum = idx + 1

    if (boxNum > MAX_LEITNER_BOX):
        return chooseLeitnerBox(cProbs)

    return boxNum

def AllBoxesEmpty(boxes):
    for box in boxes:
        if not box.isEmpty():
            return False
    return True

def moveLeitnerBoxUp(q, db, leitnerBoxes):
    currentBox = int(q.box)
    newBox = currentBox + 1
    # make sure not to move question beyond max
    if(currentBox != MAX_LEITNER_BOX):
        q.box = newBox
        # change question in Lboxes
        leitnerBoxes[currentBox - 1].removeQuestion(q)
        leitnerBoxes[newBox - 1].addQuestion(q)

        # change Lbox in csv, dictionary
        db.editDBLeitnerBox(q, newBox, 1)

def moveLeitnerBoxDown(q, db, leitnerBoxes):
    currentBox = int(q.box)
    # make sure not to move down past 1st box
    if (currentBox != FIRST_LEITNER_BOX):
        newBox = currentBox - 1
        q.box = newBox
        # change question in Lboxes
        leitnerBoxes[currentBox - 1].removeQuestion(q)
        leitnerBoxes[newBox - 1].addQuestion(q)

        # change box in csv, dictionary
        db.editDBLeitnerBox(q, newBox, 1)


def printEndQuiz():
    print
    print "Don't get cocky."
    print
    
#########################################################################
""" ---------------------- Leitner Box Class ------------------------ """
#########################################################################

class LeitnerBox:
    def __init__(self,
                 box_Number,
                 box_Questions):
        self.boxNumber = box_Number
        self.boxQuestions = box_Questions

    # add  question
    def addQuestion(self, q):
        self.boxQuestions.append(q)

    # remove question
    def removeQuestion(self, q):
        for question in self.boxQuestions:
            if (question.id == q.id):
                self.boxQuestions.remove(question)

    # get random question
    def getRandomQuestion(self):
        return random.choice(boxQuestions)

    # check if box is empty
    def isEmpty(self):
        return not self.boxQuestions

    def getNumberOfQuestions(self):
        return len(self.boxQuestions)

    def printBox(self):
        print 'Leitner Box ', self.boxNumber
        for question in self.boxQuestions:
            print '\t', question.getQuestionString()


# fire it up
if __name__ == '__main__':
    main()
