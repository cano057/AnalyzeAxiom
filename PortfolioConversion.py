#Convierte un JSON que proviene directamente de Axiom en un Diccionario sencillo dispuesto para su análisis
import xlsxwriter
import json
from pathlib import Path
class PortfolioConversion():

    def __init__(self):
        #Diccionario con una condición y su correspondiente lista
        self.condition = {"var": [], "operator": "", "values": []}
        self.conditions = []
        #Variable propia del portfolio y su correspondiente lista
        self.variable = {"name": "", "models":[], "conditions": [], "formula": "", "registers": []}
        self.variables = []
        self.mappingDiccionary = {"name": "", "registers": []}
        self.mappingList = []
        #formula
        self.formula = ""
        
    #Archives
    def ls3(self, path):
        return [obj.name for obj in Path(path).iterdir() if obj.is_file()]

    def getJSON(self, folderJSON):
        archivesFiles=self.ls3(folderJSON) 
        jsonArchives = []
        for file in archivesFiles:
            if(len(file.split("_nodes")) == 1):
                jsonArchives.append(file)
                print(file)
        return jsonArchives

    def enterColumn(self, isNot, listOfValues, listOfCopulas):
        self.condition.clear()
        valorVar = []
        if listOfValues["_type"] != "EXPRESSION_FREEHAND":
            if isinstance(listOfValues["COLUMN"], list):
                for column in listOfValues["COLUMN"]:
                    valorVar.append({"alias": columns["ALIAS"], "name" : column["COLNAME"]})
            else:
                valorVar.append({"alias": listOfValues["COLUMN"]["ALIAS"], "name":listOfValues["COLUMN"]["COLNAME"]})

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
        self.formula = self.formula + "(" + " ".join(d['name'] for d in valorVar) + " " + listOfValues["OPERATION"] + " " + " ".join(values) + ")"
        if(listOfCopulas != ""):
            self.formula = self.formula + " " + listOfCopulas + " " 
        #Enter values in condition diccionary
        self.condition["var"] = valorVar
        self.condition["operator"] = ("", "NOT ")[isNot] + listOfValues["OPERATION"]
        self.condition["values"] = values
        #Enter condition into conditions list
        self.conditions.append(self.condition.copy())

    def enterValue(self, isNot, listOfValues, listOfCopulas):
        #Several Conditions
        if len(listOfValues) == 2:
            numberOfValue = 0
            self.formula = self.formula + "("
            #Gets all the Conditions
            for value in listOfValues["CONDITION"]:
                numberOfValue = self.checkCondition(value, listOfValues, numberOfValue)
            self.formula = self.formula + ")"
            if(listOfCopulas != ""):
                self.formula = self.formula + " " + listOfCopulas + " "
            #worksheet.write(i, 1, listOfCopulas)
            #i = i + 1
        elif len(listOfValues) == 1:
            self.enterColumn(isNot, listOfValues["CONDITION"], listOfCopulas)
        else:
            self.enterColumn(isNot, listOfValues, listOfCopulas)

    #En caso de haber más de una condición se comprueba la estructura de estas previo a su analisis correspondiente
    #Recorre la lista de condiciones y toma acciones dependiendo del tipo de condición que sea
    def checkCondition(self, conditionParam, columns, numberOfValue):
        isNot = False
        if isinstance(conditionParam, str):
            return
        #Check if Copula is "Not"
        if (columns["COPULA"] == "NOT"):
            numberOfValue = numberOfValue + 1
            isNot = True
            self.formula = self.formula + " NOT"
        elif (numberOfValue <= (len(columns["COPULA"]) - 1)):
            if (columns["COPULA"][numberOfValue] == "NOT"):
                isNot = True
                numberOfValue = numberOfValue + 1
                self.formula = self.formula + " NOT"
        #Normal Condition (involves other conditions)
        if((numberOfValue == 0) or (numberOfValue <= (len(columns["COPULA"])-1) and isinstance(columns["COPULA"], list))):
            #Only involves one Condition
            if(len(conditionParam) == 1):
                if(isinstance(columns["COPULA"], list)):
                    self.enterValue(isNot, conditionParam["CONDITION"], columns["COPULA"][numberOfValue])
                else:
                    self.enterValue(isNot, conditionParam["CONDITION"], columns["COPULA"])
            #Involves more than one Condition
            else:  
                if(isinstance(columns["COPULA"], list)):
                    self.enterValue(isNot, conditionParam, columns["COPULA"][numberOfValue])
                else:
                    self.enterValue(isNot, conditionParam, columns["COPULA"])
        #Last Condition
        else:
            if (len(self.condition) == 1):
                self.enterValue(isNot, conditionParam["CONDITION"], "")
            else:
                self.enterValue(isNot, conditionParam, "")
        numberOfValue = numberOfValue + 1
        return numberOfValue
    
    #Recoge las condiciones y filtros de una variable en la pestaña Actions de Nodes
    def getConditionsFromNodes(self, portfolioNode, registerName):
        self.conditions.clear()
        self.formula = ""
        for action in portfolioNode["actions"]["param"]["paramLine"]:
            self.condition.clear()
            self.condition["var"] = [action["param"][2]["string"]]
            self.condition["operator"] = "="
            self.condition["values"] = [action["param"][3]["string"]]
            self.conditions.append(self.condition.copy())
        return self.conditions.copy()
             

    #Recoge las condiciones y filtros de una variable
    def getConditions(self, conditionParam, registerName):
        self.conditions.clear()
        self.formula = ""
        if bool(conditionParam):
            numberOfValue = 0
            #Only one Condition in a list
            if (len(conditionParam["CONDITION"]) ==  1):
                isNot = False
                #Copula equal to "not"
                if(len(conditionParam) == 2):
                    isNot = True
                    self.formula = " NOT("
                self.enterValue(isNot, conditionParam["CONDITION"]["CONDITION"], "")
            #Only One condition and not a list
            elif (not(isinstance(conditionParam["CONDITION"], list)) and (len(conditionParam["CONDITION"].keys()) > 2)):
                isNot = False
                if(len(conditionParam) == 2):
                    isNot = True
                    self.formula = " NOT("
                self.enterValue(isNot, conditionParam["CONDITION"], "")  
            #More than one condition                 
            else:
                #Conditions in a list
                if isinstance(conditionParam["CONDITION"], list):
                    for condition in conditionParam["CONDITION"]:
                        #Get all the conditions for each previous condition
                        numberOfValue = self.checkCondition(condition, conditionParam, numberOfValue)
                        #i = i + 1
                #Conditions in a Dictionary of a list        
                else:
                    for condition in conditionParam["CONDITION"]["CONDITION"]:
                        numberOfValue = self.checkCondition(condition, conditionParam["CONDITION"], numberOfValue)
            print(str(self.index) + ":" + registerName)
        else:
            print("Empty " + str(self.index) + ": " + registerName)

    #Recoge los valores de cada Nodo
    def getValuesOfNode(self, portfolioNode, jsoncolumnspy):
        models = []
        conditionsTemp = []
        variableTemp = self.variable.copy()
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
        if(jsoncolumnspy):
            self.getConditions(jsoncolumnspy["JSONCOLUMNS"]["CONDITION"][self.index], variableTemp["name"])
        else:
            self.getConditionsFromNodes(portfolioNode, variableTemp["name"])
        variableTemp["conditions"] = self.conditions.copy()
        formulaTemp = ""
        formulaTemp = self.formula
        variableTemp["formula"] = formulaTemp
        variableTemp["registers"] = []
        return variableTemp

    #Recoge los nombres de cada variable a analizar
    def enterIntoNode(self, jsonNodesParameter, jsoncolumnspy):
        variablesTemp = []
        variableTemp = self.getValuesOfNode(jsonNodesParameter, jsoncolumnspy)
        self.index = self.index + 1
        #En caso de contener más variables ingresa en ellas
        if (len(jsonNodesParameter.keys()) > 10):
            if(isinstance(jsonNodesParameter["portfolio-node"], list)):
                for node in jsonNodesParameter["portfolio-node"]:
                    variablesTemp.append(self.enterIntoNode(node, jsoncolumnspy))
            else:
                variablesTemp.append(self.enterIntoNode(jsonNodesParameter["portfolio-node"], jsoncolumnspy))
        variableTemp["registers"] = variablesTemp
        return variableTemp

    #Analiza el JSON con los nombres a analizar
    def getRegistersForNodes(self, jsonNodesParameter, jsoncolumnspy):
        self.variable.clear()
        self.mappingDiccionary.clear()
        self.index = 0
        self.variable = self.enterIntoNode(jsonNodesParameter["nodes"]["portfolio-node"], jsoncolumnspy)
        return self.variable.copy()

    def convertPortfolio(self, folder):
        jsonArchives = self.getJSON("/home/cano057/VisualStudio/Axiom/" + folder)
        self.mappingList = []
        for inform in jsonArchives:
            self.mappingDiccionary.clear()
            informPath = folder + "/" + inform
            informName = inform.split(".")[0]
            print(informName)
            with open(informPath) as jsoncolumns:
                jsonArchiveNodesRegister = folder + "/" + informName + "_nodes" + ".json"
                jsoncolumnspy = json.load(jsoncolumns)
                #Get Registers from Nodes
                with open(jsonArchiveNodesRegister) as jsonRegistersNodes:
                    jsonRegisterNodespy = json.load(jsonRegistersNodes)
                    self.registers = []
                    registersFromNode = []
                    self.mappingDiccionary["registers"] = [self.getRegistersForNodes(jsonRegisterNodespy, jsoncolumnspy)]
                    self.mappingDiccionary["name"] = informName
                    self.mappingList.append(self.mappingDiccionary.copy())
        return self.mappingList
    
    def convertPortfolioActions(self, folder):
        jsonArchives = self.getJSON("/home/cano057/VisualStudio/Axiom/" + folder)
        self.mappingList = []
        for inform in jsonArchives:
            self.mappingDiccionary.clear()
            informPath = folder + "/" + inform
            informName = inform.split(".")[0]
            print(informName)
            #Get Registers from Nodes
            with open(informPath) as jsonRegistersNodes:
                jsonRegisterNodespy = json.load(jsonRegistersNodes)
                self.registers = []
                registersFromNode = []
                self.mappingDiccionary["registers"] = [self.getRegistersForNodes(jsonRegisterNodespy, [])]
                self.mappingDiccionary["name"] = informName
                self.mappingList.append(self.mappingDiccionary.copy())
        return self.mappingList.copy()