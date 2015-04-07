# DeutschLerner german database management
# Corbin Foucart

# description needed

# imports
import csv
import glob
import os
from nameConstants import *
import random
import string
import copy
import quizManager as qm

# Class definitions
###########################################################################
""" ------------------------- DICTIONARY CLASS ------------------------ """
###########################################################################

class questionDictionary:
	# constructor
	def __init__(self, dictionaryFilename):
		self.fileName     = dictionaryFilename
		self.dictionary   = self.loadDictionary(dictionaryFilename)
		self.currentGroup = None
		self.fieldNames   = ['q_questionString',
									'q_answer',
									'q_type',
									'q_groupName',
									'q_groupNumber',
									'q_LeitnerBox',
									'q_ID']


	# ---------------- initialization

	# accessing information from the database
	def loadDictionary(self, dictFile):
		dictionary = {}
		if self.csvFileExists(dictFile):
			with open(dictFile) as currFile:
				reader = csv.reader(currFile)
				for row in reader:
					question = self.getQuestionFromRow(row)
					dictionary[question.id] = question
		return dictionary

	#  -----------------  CSV manipulation ----------- #

	# takes in a row from csv reader and returns a question object
	def getQuestionFromRow(self, row):
		qString         = row[0]
		qAnswerString   = row[1]
		qIdentifier     = row[2]
		qGroup          = row[3]
		qGroupNumber    = row[4]
		qLeitnerBox     = row[5]
		qID             = row[6]
		return Question(qID,
						qIdentifier,
						qString,
						qGroup,
						qGroupNumber,
						qAnswerString,
						qLeitnerBox)

	# given a row from a reader, this function writes
	# a row to another file specified by the fileWriter
	# which is passed in. 
	def writeRow(self, fileWriter, row):
		fieldNames = self.fieldNames
		fileWriter.writerow(
			 {fieldNames[0]  : row[0],
			  fieldNames[1]  : row[1],
			  fieldNames[2]  : row[2],
			  fieldNames[3]  : row[3],
			  fieldNames[4]  : row[4],
			  fieldNames[5]  : row[5],
			  fieldNames[6]  : row[6] })

	# save entire dictionary to csv by creating a new temp csv
	# and replacing the old dictionary with the temp file
	def saveDictionaryToCSV(self):
		# check if csv file already exists and give appropriate header
		dictionary = self.dictionary
		dictFile   = self.fileName

		with open(TEMPORARY_DICT, 'w') as csvfile:
			fieldNames = self.fieldNames
			writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
			if not self.csvFileExists(TEMPORARY_DICT):
				writer.writeheader()
			for key in dictionary:
				currQuestion = dictionary[key]
				row = currQuestion.getQuestionAsRow()
				self.writeRow(writer, row)

		# copy the correction to the intended file
		os.rename(TEMPORARY_DICT, dictFile)

	def appendEntryToCSV(self, question):
		with open(DICTIONARY_NAME, 'a') as csvfile:
			fieldNames = self.fieldNames
			writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
			row = question.getQuestionAsRow()
			self.writeRow(writer, row)

	def removeEntryFromCSV(self, question):
		# removal of old group information
		removalID = question.id

		# create a corrected file with the change
		with open(TEMPORARY_DICT, 'w') as writef:
			fieldnames = self.fieldNames
			writer = csv.DictWriter(writef, fieldnames=fieldnames)
			with open(DICTIONARY_NAME) as readf:
				reader = csv.reader(readf)
				for row in reader:
					currQuestion = self.getQuestionFromRow(row)
					currID = currQuestion.id
					if (currID != removalID):
						self.writeRow(writer, row)

		# copy the correction back to the intended file by renaming it
		os.rename(TEMPORARY_DICT, DICTIONARY_NAME)		

	def removeGroupFromCSV(self, group):
		# removal of old group information
		removalIds = []
		for question in group.questions:
			removalIds.append(question.id)

		# create a corrected file with the change
		with open(TEMPORARY_DICT, 'w') as writef:
			fieldnames = self.fieldNames
			writer = csv.DictWriter(writef, fieldnames=fieldnames)
			with open(DICTIONARY_NAME) as readf:
				reader = csv.reader(readf)
				for row in reader:
					currQuestion = self.getQuestionFromRow(row)
					currID = currQuestion.id
					if not (currID in removalIds):
						self.writeRow(writer, row)

		# copy the correction back to the intended file by renaming it
		os.rename(TEMPORARY_DICT, DICTIONARY_NAME)


	# ---------------------- group related ------------------------ #

	def changeCurrentGroup(self, groupName):
		# check if group exists or not yet, and load it into memory
		# or create new one 
		if (self.groupExists(groupName)):
			self.currentGroup = self.loadGroupFromDictionary(groupName)			
		else:
			print "Group does not exist. Creating a new editing group."
			print 
			self.currentGroup = Group([], groupName)

		# check if group exists
	def groupExists(self, groupName):
		dictionary = self.dictionary
		for key in dictionary:
			qCheck = dictionary[key]
			if (qCheck.groupName == groupName):
				return True
		return False

	def loadGroupFromDictionary(self, groupName):
		dictionary    = self.dictionary
		questionsList = []
		for key in dictionary:
			currQuestion = dictionary[key]
			if (currQuestion.groupName == groupName):
				questionsList.append(currQuestion)
		return Group(questionsList, groupName)


	# --------------------- adding to database ------------------- #

	def addEntryToDB(self):
		# if no group chosen, choose one
		if (self.currentGroup == None):
			gName = str(raw_input('Enter the name of a group to edit: '))
			self.changeCurrentGroup(gName)
			
		# add question to current group
		entryQuestion = self.promptEntry()
		if (entryQuestion == None):
			return  # case where quit sentinel is entered
		self.currentGroup.addQuestion(entryQuestion)

		# add question to dictionary
		questionID = entryQuestion.id
		self.dictionary[questionID] = entryQuestion
		
		# save dictionary change to csv
		if not self.csvFileExists(DICTIONARY_NAME):
			self.saveDictionaryToCSV()
		else:
			self.appendEntryToCSV(entryQuestion)

	def promptEntry(self):
		ID         = self.generateRandomID()
		group      = self.currentGroup
		identifier = self.promptIdentifier()
		if (identifier != QUIT_SENTINEL):
			question_string = str(raw_input('English: '))
			nextGroupNumber = group.getNextQuestionNumber()

			entryQuestion = Question(ID, 
									 identifier,
									 question_string,
									 group.name,
									 nextGroupNumber)

			answer_string = entryQuestion.promptForUserAnswer()
			entryQuestion.answer = answer_string
			return entryQuestion
		else:
			return None

	 # open the accepted ids file and check the user's input
	 # against everything in that file to ferret out the
	 # appropriate id. If the id is not found, prompt the
	 # user to try again. Returns correct ID string e.g. 'N'
	def promptIdentifier(self):
		while True:
			identifier = str(raw_input('Enter type id: ')).lower()
			if self.csvFileExists(ACCEPTEDS_FILENAME):
				 with open(ACCEPTEDS_FILENAME) as f:
					  reader = csv.reader(f)
					  for row in reader:
							cand = row[0]
							if (identifier == cand):
								return row[1]
	
	# ------------------- removing/editing database ---------------------- #

	def removeEntryFromDB(self, question):
		removeID    = question.id
		removeIndex = int(question.groupNumber) - 1 

		# remove question from dictionary
		self.dictionary.pop(removeID, None)

		# remove the old group from csv
		# update group and add to csv
		oldGroup = copy.deepcopy(self.currentGroup)
		self.currentGroup.removeQuestion(removeIndex)
		newGroup = self.currentGroup

		self.removeGroupFromCSV(oldGroup)
		for q in newGroup.questions:
			self.appendEntryToCSV(q)

	def editDBEntry(self, question):
		newQuestion  = copy.deepcopy(question)
		editQuestion = self.promptEntry()
		
		# reassign salient properties of new question
		newQuestion.type      = editQuestion.type
		newQuestion.question  = editQuestion.question
		newQuestion.answer    = editQuestion.answer 

		self.removeEntryFromCSV(question)
		self.appendEntryToCSV(newQuestion)
		
		index = int(question.groupNumber) - 1
		qID   = question.id
		self.currentGroup.questions[index] = newQuestion
		self.dictionary[qID] = newQuestion

	# editing the leitner box information from a 
	# database side. changes the box number in 
	# the group, dictionary, and in the csv file,
	# but is not the method used when actually
	# doing the pruning quiz.
	def editDBLeitnerBox(self, question, newBox, editGroup=0):
		editedQuestion     = copy.deepcopy(question)
		editedQuestion.box = newBox

		# edit in csv file
		self.removeEntryFromCSV(question)
		self.appendEntryToCSV(editedQuestion)

		# edit in working memory
		index = int(question.groupNumber) - 1
		qID   = question.id
		if (editGroup == 0):
			self.currentGroup.questions[index] = editedQuestion
			self.dictionary[qID] = editedQuestion 

	# ----------------  Leitner Box stuff ----------------------- #	

	def getLeitnerBoxArray(self):
		dictionary = self.dictionary
		leitnerArray       = []
		leitnerStagingArea = []
		leitnerUnasked     = []
		for i in range(MAX_LEITNER_BOX):
			TLB = qm.LeitnerBox(i + 1, [])
			leitnerArray.append(TLB)

		for key in dictionary:
			tQ = dictionary[key]
			boxNum = int(tQ.box)
			if (boxNum > LEITNER_STAGING_AREA):
				leitnerArray[boxNum -1].addQuestion(tQ)
			elif (boxNum == LEITNER_STAGING_AREA):
				leitnerStagingArea.append(tQ)
			elif (boxNum == LEITNER_NOT_ASKED):
				leitnerUnasked.append(tQ)

		leitnerReturnArray = [leitnerArray,
		                      leitnerStagingArea,
		                      leitnerUnasked]

		return leitnerReturnArray

	# ---------------- general helper methods ------------------- #
	 
	 # Helper method to check the existence of a given csv file
	def csvFileExists(self, csvFile):
	  return os.path.isfile(csvFile)

	# generate a random ID for each entry
	def generateRandomID(self):
		while True:
			candidate = ''.join(random.choice(string.ascii_uppercase) \
				for i in range(ID_LENGTH))

			if not (candidate in self.dictionary):
				return candidate

	def printDictionary(self):
		if not self.dictionary:
			print
			print "Dictionary is empty."

		counter = 1
		for key in self.dictionary:
			pStr    = (str(counter) + '.').ljust(4)[:4]
			pStr    += self.dictionary[key].getQuestionString(PRINT_Q_DICT)
			print pStr
			counter += 1

######################################################################
""" ------------------------- GROUP CLASS ------------------------ """
######################################################################
class Group:
	def __init__(self, groupQuestions, groupName):
		self.questions  = groupQuestions 
		self.nQuestions = len(groupQuestions)
		self.name       = groupName
		self.sortQuestions()

	def sortQuestions(self):
		self.questions.sort(key=lambda x:int(x.groupNumber), reverse=False)

	def getNextQuestionNumber(self):
		return self.nQuestions + 1

	def addQuestion(self, question):
		self.questions.append(question)
		self.nQuestions += 1
		self.sortQuestions()

	def printGroup(self):
		self.sortQuestions()
		print 
		print 'Group ', self.name
		if not self.questions:
			print '[None]'
		for question in self.questions:
			print question.getQuestionString()

	def removeQuestion(self, index):
		# remove question
		del self.questions[index] 

		# renumber questions
		counter = 1
		for question in self.questions:
			question.groupNumber = counter
			counter += 1

		self.sortQuestions()
		self.nQuestions = len(self.questions)

#########################################################################
""" ------------------------ QUESTION CLASS ------------------------- """
#########################################################################

class Question:
	def __init__(self,
				 qID,
				 qIdentifier,
				 qString,
				 qGroupName,
				 qGroupNumber,
				 qAnswerString='',
				 qLeitnerBox=LEITNER_NOT_ASKED):
		self.id           = qID
		self.groupName    = qGroupName
		self.groupNumber  = qGroupNumber
		self.type         = qIdentifier
		self.question     = qString
		self.answer       = qAnswerString
		self.box          = qLeitnerBox

	def getQuestionAsRow(self):
		row = []
		row.append(self.question)
		row.append(self.answer)
		row.append(self.type)
		row.append(self.groupName)
		row.append(self.groupNumber)
		row.append(self.box)
		row.append(self.id)
		return row

	# print out the salient aspects of the question with nice 
	# padding / formatting
	def getQuestionString(self, numberOption=0):
		rStr = ''
		if (numberOption == 0):
			rStr +=  (str(self.groupNumber)+'.').ljust(4)[:4]
		rStr += self.answer.decode('utf-8').ljust(20, ' ')[:20]   + '|'  \
		     + self.question.decode('utf-8').ljust(25, ' ')[:25] + ' |'  \
		     #+ self.id.ljust(5)[:5]                    + '|' \
		rStr += self.groupName.ljust(3)[:3]                + '|' \
			  + str(self.box).ljust(3)[:3]             + '|'
		return rStr

	# split the answer string into an array using commas
	# as delimiters. Potentially a different length for
	# each identifier type.
	def getAnswerArray(self):
		answerArray = [x.strip() for x in self.answer.split(',')]
		return answerArray

	# prompts user to supply an answer consistent with the
	# question type. Used both when setting the question
	# and when the user takes the quiz.
	def promptForUserAnswer(self):
		Qtype = self.type
		answerStr = ''
		if (Qtype == NOUN_ID):
			sing = str(raw_input('Article + singular form: ')).strip()
			plural = str(raw_input('Plural form: ')).strip()
			answerStr = sing + ', ' + plural
		if (Qtype == REG_VERB_ID):
			verb = str(raw_input('Present infinitive: ')).strip()
			answerStr = verb
		if (Qtype == IRREG_VERB_ID):
			pres = str(raw_input('Present infinitive: ')).strip()
			presth = str(raw_input('3rd person present: ')).strip()
			simP = str(raw_input('Simple past: ')).strip()
			pp = str(raw_input('Past perfect: ')).strip()
			answerStr = pres + ', ' + presth + ', ' + simP + ', ' + pp
		if (Qtype == ADJECTIVE_ID):
			answerStr = str(raw_input('German: ')).strip()
		if (Qtype == PREP_ID):
			prep = str(raw_input('Preposition: ')).strip()
			takes = str(raw_input('Case: ')).strip()
			answerStr = prep + ', ' + takes
		if (Qtype == PHRASE_ID):
			answerStr = str(raw_input('German: ')).strip()
		if (Qtype == VERB_PREP_ID):
			verb = str(raw_input('Present infinitive phrase: ')).strip()
			prep = str(raw_input('Preposition: ')).strip()
			takes = str(raw_input('Case: ')).strip()
			answerStr = verb + ', ' + prep + ', ' + takes
		return answerStr