#Convierte un JSON que proviene directamente de Axiom en un Diccionario sencillo dispuesto para su análisis
import xlsxwriter
import json
from pathlib import Path

#Diccionario con una condición y su correspondiente lista
condition = {"var": [], "operator": "", "values": []}
conditions = []
#Variable propia del portfolio y su correspondiente lista
variable = {"name": "", "models":[], "conditions": [], "formula": "", "variables": []}
variables = []
mappingDiccionary = {"name": "", "registers": {}}
mappingList = []
#formula
formula = ""
#Archives
def __init__(self):
    #Diccionario con una condición y su correspondiente lista
    self.condition = {"var": [], "operator": "", "values": []}
    self.conditions = []
    #Variable propia del portfolio y su correspondiente lista
    self.variable = {"name": "", "models":[], "conditions": [], "formula": "", "variables": []}
    self.variables = []
    self.mappingDiccionary = {"name": "", "registers": {}}
    self.mappingList = []
    #formula
    self.formula = ""

def ls3(path):
    return [obj.name for obj in Path(path).iterdir() if obj.is_file()]

archivesFiles=ls3("/home/cano057/VisualStudio/Axiom/mapping") 
jsonArchives = []
for file in archivesFiles:
    if(len(file.split("_nodes")) == 1):
        jsonArchives.append(file)
        print(file)
def enterColumn(isNot, listOfValues, listOfCopulas):
    global condition
    global conditions
    global formula
    condition.clear()
    valorVar = []
    if listOfValues["_type"] != "EXPRESSION_FREEHAND":
        if isinstance(listOfValues["COLUMN"], list):
            for column in listOfValues["COLUMN"]:
                valorVar.append(column["COLNAME"])
        else:
            valorVar.append(listOfValues["COLUMN"]["COLNAME"])

        values = []
        if isinstance(listOfValues["VALUE"], list):
            definition = []
            if (listOfValues["_type"] == "DATE_INTERVAL_REGULAR"):
                definition = [" year ", " month ", " day "]
            def_iterator = iter(definition)
            for value in listOfValues["VALUE"]:
                values.append(value + next(def_iterator, ""))
        else:
            values.append(listOfValues["VALUE"])
    #Enter formula in formula attribute
    formula = formula + "(" + " ".join(valorVar) + " " + listOfValues["OPERATION"] + " " + " ".join(values) + ")"
    if(listOfCopulas != ""):
        formula = formula + " " + listOfCopulas + " " 
    #Enter values in condition diccionary
    condition["var"] = valorVar
    condition["operator"] = ("", "NOT ")[isNot] + listOfValues["OPERATION"].replace("<=","minor or equal").replace('=', " equal")
    condition["values"] = values
    #Enter condition into conditions list
    conditions.append(condition.copy())

def enterValue(isNot, listOfValues, listOfCopulas):
    global formula
    #Several Conditions
    if len(listOfValues) == 2:
        numberOfValue = 0
        formula = formula + "("
        #Gets all the Conditions
        for value in listOfValues["CONDITION"]:
            numberOfValue = checkCondition(value, listOfValues, numberOfValue)
        formula = formula + ")"
        if(listOfCopulas != ""):
            formula = formula + " " + listOfCopulas + " "
        #worksheet.write(i, 1, listOfCopulas)
        #i = i + 1
    elif len(listOfValues) == 1:
        enterColumn(isNot, listOfValues["CONDITION"], listOfCopulas)
    else:
        enterColumn(isNot, listOfValues, listOfCopulas)

#En caso de haber más de una condición se comprueba la estructura de estas previo a su analisis correspondiente
#Recorre la lista de condiciones y toma acciones dependiendo del tipo de condición que sea
def checkCondition(conditionParam, columns, numberOfValue):
    global formula
    isNot = False
    if isinstance(conditionParam, str):
        return
    #Check if Copula is "Not"
    if (columns["COPULA"] == "NOT"):
        numberOfValue = numberOfValue + 1
        isNot = True
        formula = formula + " NOT"
    elif (numberOfValue <= (len(columns["COPULA"]) - 1)):
        if (columns["COPULA"][numberOfValue] == "NOT"):
            isNot = True
            numberOfValue = numberOfValue + 1
            formula = formula + " NOT"
    #Normal Condition (involves other conditions)
    if((numberOfValue == 0) or (numberOfValue <= (len(columns["COPULA"])-1) and isinstance(columns["COPULA"], list))):
        #Only involves one Condition
        if(len(conditionParam) == 1):
            if(isinstance(columns["COPULA"], list)):
                enterValue(isNot, conditionParam["CONDITION"], columns["COPULA"][numberOfValue])
            else:
                enterValue(isNot, conditionParam["CONDITION"], columns["COPULA"])
        #Involves more than one Condition
        else:  
            if(isinstance(columns["COPULA"], list)):
                enterValue(isNot, conditionParam, columns["COPULA"][numberOfValue])
            else:
                enterValue(isNot, conditionParam, columns["COPULA"])
    #Last Condition
    else:
        if (len(condition) == 1):
            enterValue(isNot, conditionParam["CONDITION"], "")
        else:
            enterValue(isNot, conditionParam, "")
    numberOfValue = numberOfValue + 1
    return numberOfValue

#Recoge las condiciones y filtros de una variable
def getConditions(conditionParam, registerName):
    global conditions
    global formula
    conditions.clear()
    formula = ""
    #print("index: " + str(index))
    if bool(conditionParam):
        numberOfValue = 0
        #Only one Condition in a list
        if (len(conditionParam["CONDITION"]) ==  1):
            isNot = False
            #Copula equal to "not"
            if(len(conditionParam) == 2):
                isNot = True
                formula = " NOT("
            enterValue(isNot, conditionParam["CONDITION"]["CONDITION"], "")
        #Only One condition and not a list
        elif (not(isinstance(conditionParam["CONDITION"], list)) and (len(conditionParam["CONDITION"].keys()) > 2)):
            isNot = False
            if(len(conditionParam) == 2):
                isNot = True
                formula = " NOT("
            enterValue(isNot, conditionParam["CONDITION"], "")  
        #More than one condition                 
        else:
            #Conditions in a list
            if isinstance(conditionParam["CONDITION"], list):
                for condition in conditionParam["CONDITION"]:
                    #Get all the conditions for each previous condition
                    numberOfValue = checkCondition(condition, conditionParam, numberOfValue)
                    #i = i + 1
            #Conditions in a Dictionary of a list        
            else:
                for condition in conditionParam["CONDITION"]["CONDITION"]:
                    numberOfValue = checkCondition(condition, conditionParam["CONDITION"], numberOfValue)
        print(str(index) + ":" + registerName)
    else:
        print("Empty " + str(index) + ": " + registerName)

#Recoge los valores de cada Nodo
def getValuesOfNode(portfolioNode, jsoncolumnspy):
    global variable
    global formula
    models = []
    conditionsTemp = []
    variableTemp = variable.copy()
    #Recoge Name y Models
    name = portfolioNode["_name"]
    variableTemp["name"] = name
    if(isinstance(portfolioNode["models"]["model"], list)):
        for model in portfolioNode["models"]["model"]:
            models.append(model)
    else:
        models.append(portfolioNode["models"]["model"])
    variableTemp["models"] = models
    #Recoge las condiciones y filtros de la variables a partir del otro JSON
    getConditions(jsoncolumnspy["JSONCOLUMNS"]["CONDITION"][index], variableTemp["name"])
    print(len(conditions.copy()))
    variableTemp["conditions"] = conditions.copy()
    formulaTemp = ""
    formulaTemp = formula
    variableTemp["formula"] = formulaTemp
    return variableTemp

#Recoge los nombres de cada variable a analizar
def enterIntoNode(jsonNodesParameter, jsoncolumnspy):
    global index
    variableTemp = getValuesOfNode(jsonNodesParameter, jsoncolumnspy)
    variablesTemp = []
    index = index + 1
    #En caso de contener más variables ingresa en ellas
    if (len(jsonNodesParameter.keys()) > 10):
        if(isinstance(jsonNodesParameter["portfolio-node"], list)):
            for node in jsonNodesParameter["portfolio-node"]:
                variablesTemp.append(enterIntoNode(node, jsoncolumnspy))
        else:
            variablesTemp.append(enterIntoNode(jsonNodesParameter["portfolio-node"], jsoncolumnspy))
    variableTemp["variables"] = variablesTemp
    return variableTemp

#Analiza el JSON con los nombres a analizar
def getRegistersForNodes(jsonNodesParameter, jsoncolumnspy):
    global variable
    global registersFromNode
    global index
    global mappingDiccionary
    variable.clear()
    mappingDiccionary.clear()
    index = 0
    variable = enterIntoNode(jsonRegisterNodespy["nodes"]["portfolio-node"], jsoncolumnspy)
    return variable.copy()

mappingList = []
for inform in jsonArchives:
    mappingDiccionary.clear()
    informPath = "mapping/" + inform
    informName = inform.split(".")[0]
    print(informName)
    with open(informPath) as jsoncolumns:
        jsonArchiveNodesRegister = "mapping/" + informName + "_nodes" + ".json"
        jsoncolumnspy = json.load(jsoncolumns)
        #Get Registers from Nodes
        with open(jsonArchiveNodesRegister) as jsonRegistersNodes:
            jsonRegisterNodespy = json.load(jsonRegistersNodes)
            registers = []
            registersFromNode = []
            mappingDiccionary["registers"] = getRegistersForNodes(jsonRegisterNodespy, jsoncolumnspy)
            mappingDiccionary["name"] = informName
            mappingList.append(mappingDiccionary.copy())

with open('mapping/mappingList.json', 'w') as fp:
    json.dump(mappingList, fp)