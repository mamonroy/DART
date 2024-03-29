import inspect
import importlib
import regression
import os
from os import path
import graphs

listOfStandAloneFunctions = []
listOfClasses = []
listOfMethodsInAClass = {}
temp = []
directedGraph = graphs.Graphs()


# Lists of Functions that need to be tested because of dependency
testDependencySets = set()

def isFunctionHeader(block) -> bool:
	if(block[0:3] == "def"):
		return True
	return False

def checkStandAloneFuncs(path):
	file = open(path)
	file = file.readlines()

	for lineNum, block in enumerate(file):
		  if(isFunctionHeader(block)):
		    index = 0
		    for char in block:
		    	if(char == "("):
		    		break
		    	index += 1
		    listOfStandAloneFunctions.append(block[4:index]) 
   	
def isClassHeader(block) -> bool:
	if(block[0:5] == "class"):
		return True;
	return False;

def checkForClasses(path):
	file = open(path)
	file = file.readlines()

	for lineNum, block in enumerate(file):
		if(isClassHeader(block)):
		    className = block[6:-2]
		    listOfClasses.append(className)

# Checks if there are dependancy insides functions
def checkForSAFuncsDependency(module):
	for function in listOfStandAloneFunctions:
		print("-----------------------------")
		print("Function called is: ", function)
		funcObj = getattr(module, function)
		blocks = inspect.getclosurevars(funcObj)
		for instruction in blocks[1]:
			if(instruction in listOfStandAloneFunctions):
				testDependencySets.add(function)
				testDependencySets.add(instruction)
				directedGraph.addEdges((instruction, function))
				#print(function, "is dependent on", instruction)						# For Debugging purposes

def checkMethodsInsideClass(module):
	for class_ in listOfClasses:
		classObj = getattr(module, class_)
		classMethodsSet = inspect.getmembers(classObj, inspect.isfunction)
		listOfMethodsInAClass[class_] = classMethodsSet

def extractMethodsFromSet(ArraysOfSet) -> [str]:

	temp.clear()

	for set_ in ArraysOfSet:
		temp.append(set_[0])

	return temp

def checkForDependencyinMethodsClass(module):
	for className, methodSet in listOfMethodsInAClass.items():
		print("-----------------------------")
		print("Class called is: ", className)
		for nameMethod, objMethod in methodSet:
			blocks = inspect.getclosurevars(objMethod)
			for instruction in blocks[3]:
				methods = extractMethodsFromSet(listOfMethodsInAClass[className])
				if(instruction in methods):
					testDependencySets.add(className + "." + nameMethod)
					testDependencySets.add(className + "." + instruction)
					directedGraph.addEdges((instruction, nameMethod))
					#print(nameMethod, "is dependent on", instruction)					# For Debugging purposes

def main():

	############## INPUT ############################
	originalInput = input('Please enter the path of the original file: ')
	modifiedInput = input('Please enter tha path of the modified file: ')

	originalInput = "./sample/standaloneFunctions/original/test.py"
	modifiedInput = "./sample/standaloneFunctions/original/test.py"

	if(not path.exists(originalInput) or not path.exists(modifiedInput)):
		print("Files do not exists")
		return

	################ DEPENDANCY SCANNER STARTS #############################
	print("Dependency Check Starts")
	spec = importlib.util.spec_from_file_location("test", originalInput)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)

	############## FOR STANDALONE FUNCTIONS ONLY ############################
	checkStandAloneFuncs(originalInput)
	checkForSAFuncsDependency(module)

	############## FOR CLASSES FUNCTIONS ONLY ###############################
	checkForClasses(originalInput)
	checkMethodsInsideClass(module)
	checkForDependencyinMethodsClass(module)

	# print("---------------------------------------------")
	print("Here are the methods that need to be tested: ")
	print(testDependencySets,"\n\n")

	############ REGRESSION STARTS BASED ON DEPENDENCY #########################
	fileName = os.path.basename(originalInput)  				
	locationOriginal = os.path.dirname(originalInput) + "/"   		
	locationModified = os.path.dirname(modifiedInput)  + "/"

	regression.regTest(locationOriginal, locationModified, fileName , list(testDependencySets))

	# Draw the directed Graph Diagramg
	directedGraph.draw()
				    		
if __name__ == "__main__":
    main()