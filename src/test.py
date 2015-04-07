# testing file
# Corbin Foucart

import germanDatabase as db

qD = db.questionDictionary('dictionary.csv')

qD.printDictionary()
qD.changeCurrentGroup('1')
qD.currentGroup.printGroup()
print qD.currentGroup.nQuestions

