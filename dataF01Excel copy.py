import xlsxwriter
import json
from pathlib import Path

#Variables Globales
i = 2
j =0
#Registros nodos
registros01 = ["F_01_01", "position", "300", "current_assets", "010", "030", "040", "050", "060", "070", "080", "090", "096", "097", "098", "099", "100", "120", "130", "141", "142", "143", "144", "181", "182", "183", "240", "250", "260", "360", "370", "OAL", "380", "Current_assets", "010", "20", "260", "270", "280", "290", "300", "310", "320", "330", "340", "350", "370", "360"]
registros02 = ["F_01_02", "position", "300", "current_assets", "010", "020", "030", "040", "050", "060", "070", "080", "090", "100", "110", "120", "130", "140", "150", "160", "280", "290", "OAL", "300", "Current_assets", "170","180", "190", "200", "210", "220", "230", "240", "250", "260", "270", "280", "290"]
registros03 = ["F_01_03", "300", "current_assets", "010", "030", "020", "040", "050", "060", "070", "080", "090", "095", "100", "110", "120", "124", "320", "128", "130", "140", "150", "155", "165", "180", "190", "200", "210", "220", "230", "240", "250", "260", "270", "280", "290", "non current_assets", "122", "170", "330", "340", "350", "360"]
registros0901 = ["F09_01_01", "010", "030", "021", "Others", "040", "021", "Others", "050", "021", "Others", "060", "021", "Others", "070", "021", "Others", "080", "021", "Others", "090", "110", "101", "Others", "120", "101", "Others", "130", "101", "Others", "140", "101", "Others", "150", "101", "Others", "160", "101", "Others", "170", "190", "181", "Others", "200", "181", "Others", "210", "181", "Others", "220", "181", "Others", "230", "181", "Others", "240", "181", "Others"]
registros0902 = ["F09_02", "010", "020", "030", "040", "050","060", "070", "080", "090","100", "110", "120", "130", "140", "150", "160", "170", "180", "190", "200", "210"]
registers = []
registersFromNode = []
aggregationNames = ["mapping", "Position", "OAL", "CounterParty", "Entity", "Facility", "Fx Rates", "Instrument", "Pl Movements", "Position Extended", "Position Movements", "ProfitLoss", "Entity Hierarchy", "Country", "OALMovements"]
origin = ""

#Listado de Variables obtenidas {Variable en Axiom : Variable origen}
axiomVar = {}
axiomVarReport = {}

def getRegisterName():
    registerOption = ""
    registerName = ""
    registerName = input("Teclee el nombre del archivo txt con los registros \n")
    registerName = modifyFormat(registersName, ".txt")
    return registerName

def getRegistersForConsole():
    registers = []
    registerName = getRegisterName
    while (registerOption == "archivo" or registerOption == "consola"):
        registersOption = input("Diga como introducir los registros: archivo o consola \n")
        print (" por favor, diga archivo o consola")
    if registerOption == "archivo":
        registersName = input("Teclee el nombre del archivo txt con los registros \n")
        registerName = modifyFormat(registersName, ".txt")
        try:
            f = open(registersName, "r")
            registers = f.read()
        except:
            print ("wrong file name, please enter again \n")
            registerName = getRegisterName()
    elif registerOption == "consola":
        while (valor != "end"):
            valor = input("escriba el siguiente valor o end para terminar \n")
            registers.append(valor)
    return registerName

def enterIntoNode(jsonNodesParameter):
    global registersFromNode
    name = jsonNodesParameter["_name"]
    registersFromNode.append(name)
    if (len(jsonNodesParameter.keys()) > 10):
        if(isinstance(jsonNodesParameter["portfolio-node"], list)):
            for node in jsonNodesParameter["portfolio-node"]:
                enterIntoNode(node)
        else:
            enterIntoNode(jsonNodesParameter["portfolio-node"])

def getRegistersForNodes(jsonNodesParameter):
    global registersFromNode
    with open(jsonNodesParameter) as jsonRegistersNodes:
        jsonRegisterNodespy = json.load(jsonRegistersNodes)  
        enterIntoNode(jsonRegisterNodespy["nodes"]["portfolio-node"])
          
        

def modifyFormat(stringValue, formatValue):
    if(((stringValue[(len(stringValue)- len(formatValue)) :]) != formatValue) or ((len(stringValue)- len(formatValue)) <= 0)):
        print (stringValue + formatValue)
        return (stringValue + formatValue)
    else:
        print ("correct format")
        return stringValue
def getJsonArchives():
    jsonArchives = []
    valor = ""
    while (valor != "end"):
        valor = input("escriba el nombre del archivo: \n")
        if(valor != "end"):
            valor = modifyFormat(valor, ".json")
            jsonArchives.append(valor)
    return jsonArchives  

def ls3(path):
    return [obj.name for obj in Path(path).iterdir() if obj.is_file()]

#Variables a leer
archivesFiles=ls3("/home/cano057/VisualStudio/Axiom/archives") 
jsonArchives = []
for file in archivesFiles:
    if(len(file.split("_nodes")) == 1):
        jsonArchives.append(file)
        print(file)
#jsonArchive = input("Teclee el nombre del archivo JSON que contenga los filtros \n")
#jsonArchive = modifyFormat(jsonArchive, ".json")
#jsonArchives = getJsonArchives()
jsonArchiveNodes = input("Teclee el nombre del archivo JSON que contenga los nodos \n")
jsonArchiveNodes = modifyFormat(jsonArchiveNodes, ".json")
jsonArchivePosition = "PositionAggregation.json"
jsonArchiveOAL = "OALAggregation.json"
workbookName = input("Tecle el nombre del archivo xlsx de salida \n")
workbookName = modifyFormat(workbookName, ".xls")

valuesTaken = ""
cuenta = 0
formula = ""

#workSheet Reporte
workbook = xlsxwriter.Workbook(workbookName)
xlsxwriter.Workbook(workbook, {'strings_to_numbers' : False , 'strings_to_formulas' : True , 'strings_to_urls' : True})
header_format = workbook.add_format({'bold': True,'border': 6,'align': 'center','valign': 'vcenter','fg_color': '#999999'})

for inform in jsonArchives:
    axiomVarReport.clear()
    informPath = "archives/" + inform
    informName = inform.split(".")[0]
    print(informName)
    with open(informPath) as jsoncolumns:
        jsonArchiveNodesRegister = "archives/" + informName + "_nodes" + ".json"
        jsoncolumnspy = json.load(jsoncolumns)

        worksheet = workbook.add_worksheet(informName)

        worksheet.write(0, 0, "register name", header_format)
        #worksheet.write(1, 1, "Yes or Not")
        worksheet.write(0, 1, "Origen", header_format)
        worksheet.write(0, 2, "var", header_format)
        worksheet.write(0, 3, "operator", header_format)
        worksheet.write(0, 4, "value", header_format)
        worksheet.write(0, 5, "Type of Operation", header_format)
        worksheet.write(0, 6, "Colname", header_format)
        worksheet.write(0, 7, "Alias", header_format)
        worksheet.write(0, 8, "Operation", header_format)
        worksheet.write(0, 9, "Value", header_format)
        worksheet.write(0, 10, "Copula", header_format)
        worksheet.write(0, 11, "Formula", header_format)
        worksheet.freeze_panes(1, 1)

        def newAggregationSheet(name):
            workAggregationSheet = workbook.add_worksheet(name)
            workAggregationSheet.write(0, 0, "Variable", header_format)
            workAggregationSheet.write(0, 1, "Data Staging", header_format)
            workAggregationSheet.write(0, 2, "Data Enrichment", header_format)
            workAggregationSheet.write(0, 3, "Direct Mapping", header_format)
            workAggregationSheet.write(0, 4, "Origen", header_format)
            workAggregationSheet.write(0, 5, "Expression", header_format)
            workAggregationSheet.write(0, 6, "Variable", header_format)
            workAggregationSheet.write(0, 7, "Origen", header_format)
            workAggregationSheet.write(0, 8, "Dependencias", header_format)
            indexSheet = 9
            for inform in jsonArchives:
                workAggregationSheet.write(0, indexSheet, "Está en " + informName, header_format) 
                indexSheet = indexSheet + 1
            workAggregationSheet.freeze_panes(1, 1)
            return workAggregationSheet

        #Get the Operator variables from an operation
        def getOperators(operation):
            operationSplitted = operation.split(" + ")


        def getVariable(expression):
            variables = []                
            varDivThen = expression.split("THEN")
            if(len(varDivThen) == 1):
                varDivThen = expression.split("then")
            if(len(varDivThen) > 1):
                for var in varDivThen:
                    if var[0:2] == " $":
                        variables.append(var.split(" ")[1].split(".")[1])
                    if var[0:2] == " '":
                        variables.append(var.split(" ")[1].replace("'", '"'))
            else:
                for variable in expression.split(" "):
                    varDivPoint = variable.split(".")
                    if(len(varDivPoint) > 1):
                        variables.append(varDivPoint[1])
                    else:
                        if ((variable.find("+") == -1) and (variable.find("*") == -1) and (variable.find("-") == -1)):
                            variables.append(variable.replace("'", '"'))
            variables = list(dict.fromkeys(variables))
            return variables
        
        def getVariableOrigin(expression):
            variables = []
            varDivThen = expression.split("THEN")
            if(len(varDivThen) > 1):
                varDivThen = expression.split("then")
            if(len(varDivThen) > 1):
                for var in varDivThen:
                    if var[0:2] == " $":
                        variables.append(var.split(" $")[1].split(".")[0])
            else:
                for variable in expression.split(" "):
                    varDivPoint = variable.split("$")
                    if(len(varDivPoint) > 1):
                        variables.append(varDivPoint[1].split(".")[0])
            variables = list(dict.fromkeys(variables))
            return variables         

        def getDependencies(expression):
            dependencies = []
            origins = []
            pos = expression.find('$')
            while(pos >= 0):
                if(len(expression[pos:].split(".")) > 1):
                    variable = expression[pos:].split(".")[1]
                    origin = expression[pos:].split(".")[0]
                    if(len(variable.split(" ")[0]) > 1):
                        variable = variable.split(" ")[0]
                        if(variable[-1] == ","):
                            variable = variable[0:-1]
                        if(variable.find('=') >= 0):
                            variable = variable.split('=')[0]
                    dependencies.append(variable)
                    origins.append(origin)
                pos = expression.find('$', pos+1, len(expression))
            dependencies = list(dict.fromkeys(dependencies))
            origins = list(dict.fromkeys(origins))
            return origins, dependencies


        def enterPortfolio(portfolio):
            name = portfolio["_name"]
            for register in registers:
                if register == name:
                    for model in portfolio["models"]:
                        origin[register] = origin[register] + " \n " + model
            try:
                for nodes in portfolio["portfolio-node"]:
                    enterPortfolio(nodes)
            except:
                print("no more nodes in this portfolio")
            
        #Gets the Origin from the Json Archive
        def enterOrigin():
            with open(jsonArchiveNodesRegister) as jsonRegister:
                jsonRegisterpy = json.load(jsonRegister)
                enterPortfolio(jsonRegisterpy["nodes"]["portfolio-node"])

        #Gets the Origin from the Register List
        def getOrigin(register):
            if register == "position":
                return "position"
            elif register == "OAL":
                return "Oter Assets Liabilities"
            else:
                return ""

        #Concatenate Value if existed
        def addValue(key, value, dictionary):
            if dictionary[key] == "":
                return value
            else:
                return dictionary[key] + "." + value

        #Analyze the Model Attribute to get the different Origins
        def analyzeOrigin(models):
            listOfModels = {"DM":"" , "DE":"" , "DS":""}
            isDE = False
            for model in models.split("."):
                if len(model.split("Data_Enrichment")) > 1:
                    isDE = True
                    modelSplitted = model.split(":")
                    listOfModels["DE"] = addValue("DE", modelSplitted[1], listOfModels)
                elif isDE:
                    listOfModels["DS"] = addValue("DS", model, listOfModels)
                else:
                    listOfModels["DM"] = addValue("DM", model, listOfModels)
            return listOfModels

        def enterFormula(listElement,listOfCopulas, workSheetParam, index, firsPosition, variable, origin):
            workSheetParam.write(index, 0, variable)
            workSheetParam.write(index, 1, origin)
            workSheetParam.write(index, firsPosition, listElement["_type"])
            workSheetParam.write(index, (firsPosition + 1), listElement["COLUMN"]["COLNAME"])
            workSheetParam.write(index, (firsPosition + 2), listElement["COLUMN"]["ALIAS"])
            workSheetParam.write(index, (firsPosition + 3), listElement["OPERATION"])
            if isinstance(listElement["VALUE"], list):
                values = ""
                for value in listElement["VALUE"]:
                    values = values + " " + value
                workSheetParam.write(index, (firsPosition + 4), values)
            else:
                workSheetParam.write(index, (firsPosition + 4), listElement["VALUE"])
            workSheetParam.write(index, (firsPosition + 5), listOfCopulas)
            indexn = index + 1
            return indexn

        def enterIntoList(pos, listElement, listOfCopulas, workSheetParam, index, firsPosition, variable, origin):
            indexn = index
            global cuenta            
            for keys in listElement:
                if keys == "CONDITION":
                    numOfVar = 0

                    for element in listElement["CONDITION"]:
                        if (numOfVar < (len(listElement["CONDITION"])-1)):
                            if(len(listElement["CONDITION"]) > 2):
                                indexn = enterIntoList(True, element, listElement["COPULA"][numOfVar], workSheetParam, indexn, firsPosition, variable, origin)
                            else: 
                                indexn = enterIntoList(True, element, listElement["COPULA"], workSheetParam, indexn, firsPosition, variable, origin)
                        else:
                            index = enterIntoList(True, element,"", workSheetParam, indexn, firsPosition, variable, origin)
                        numOfVar = numOfVar + 1
                    
                    workSheetParam.write(indexn, 0, variable)
                    workSheetParam.write(indexn, 1, origin)
                    workSheetParam.write(indexn, (firsPosition + 5), listOfCopulas)
                    if(pos):
                        indexn = index + 1
                    break
                elif keys != "COPULA":
                    indexn = enterFormula(listElement, listOfCopulas, workSheetParam, indexn, firsPosition, variable, origin)
                    cuenta = cuenta + 1
                    break
            return indexn
            
        #Get Expression from Attributes
        def mappingAttributes(index, firsPosition, valuesTakenParam, workSheetParam, variable, origin):
            indexn = index
            with open(jsonArchiveNodes) as jsonNodes:
                jsonNodespy = json.load(jsonNodes)
                for portfolios in jsonNodespy["nodes"]["portfolio-node"]:
                    for node in portfolios["portfolio-node"]:
                        for valorVarn in valuesTakenParam.split(" "):
                            if (valorVarn == node["_name"]):
                                if (isinstance(node["CONDITION"]["CONDITION"], list)):
                                    numOfVar = 0
                                    for condition in node["CONDITION"]["CONDITION"]:
                                        if (numOfVar < (len(node["CONDITION"]["CONDITION"])-1)): 
                                            if (isinstance(node["CONDITION"]["COPULA"], list)):
                                                indexn = enterIntoList(True, condition, node["CONDITION"]["COPULA"][numOfVar], workSheetParam, indexn, firsPosition, variable, origin)
                                            else:
                                                indexn = enterIntoList(True, condition, node["CONDITION"]["COPULA"], workSheetParam, indexn, firsPosition, variable, origin) 
                                        else:
                                            indexn = enterIntoList(True, condition, "", workSheetParam, indexn, firsPosition, variable, origin)
                                        numOfVar = numOfVar + 1

                                else:
                                    if "EXPRESSION_FREEHAND" != node["CONDITION"]["CONDITION"]["_type"]:
                                        workSheetParam.write(indexn, (firsPosition + 1), node["CONDITION"]["CONDITION"]["COLUMN"]["COLNAME"])
                                        workSheetParam.write(indexn, (firsPosition + 2), node["CONDITION"]["CONDITION"]["COLUMN"]["ALIAS"])
                                        workSheetParam.write(indexn, (firsPosition + 3), node["CONDITION"]["CONDITION"]["OPERATION"])

                                    workSheetParam.write(indexn, 0, variable)
                                    workSheetParam.write(indexn, 1, origin)
                                    workSheetParam.write(indexn, firsPosition, node["CONDITION"]["CONDITION"]["_type"])
                                    workSheetParam.write(indexn, (firsPosition + 4), node["CONDITION"]["CONDITION"]["VALUE"])
                                    for keys in node["CONDITION"]:
                                        if keys == "COPULA":
                                            workSheetParam.write(indexn, 0, variable)
                                            workSheetParam.write(indexn, 1, origin)
                                            workSheetParam.write(indexn, (firsPosition + 5), node["CONDITION"]["COPULA"])
                                    indexn = indexn + 1
                return indexn
            
        #Change the Columns Width
        def setColumnsWidth(workSheetParam):
            width = 5
            workSheetParam.set_column(0, 0, 5*width)
            workSheetParam.set_column(1, 3, 10*width)
            workSheetParam.set_column(4, 5, 20*width)

        def getValuesOfVariables(value, valueOrigin):
            global axiomVar
            for key in axiomVar.keys():
                if (value in axiomVar[key].keys()):
                    if (axiomVar[key][value] == ""):
                        axiomVar[key][value] = valueOrigin

        #Enter all the Origin and Expressions for the differents attributes in an Aggregation
        def enterAggregation(jsonArchive, workSheetParam):
            varExpression = ""
            varName = ""
            index = 1
            listOfModels = {}
            for nodes in jsonArchive["nodes"]["parameterNode"]["parameterNode"][1]["parameterNode"]:
                if (isinstance(nodes["parameters"]["param"]["paramLine"], list)):
                    for paramLine in nodes["parameters"]["param"]["paramLine"]:
                        workSheetParam.write(index, 0, nodes["_name"])
                        listOfModels = analyzeOrigin(paramLine["param"][0]["string"])
                        workSheetParam.write(index, 1, listOfModels["DS"])
                        workSheetParam.write(index, 2, listOfModels["DE"])
                        workSheetParam.write(index, 3, listOfModels["DM"])
                        workSheetParam.write(index, 4, paramLine["param"][0]["string"])
                        workSheetParam.write(index, 5, paramLine["param"][1]["string"])
                        workSheetParam.write(index, 6, " ".join(getDependencies(paramLine["param"][1]["string"])[0]))
                        workSheetParam.write(index, 7, " ".join(getVariableOrigin(paramLine["param"][1]["string"])))
                        workSheetParam.write(index, 8, " ".join(getDependencies(paramLine["param"][1]["string"])[1]))
                        #CheckValueInReport
                        getValuesOfVariables(nodes["_name"], " ".join(getDependencies(paramLine["param"][1]["string"])[1]))
                else:
                    workSheetParam.write(index, 0, nodes["_name"])
                    listOfModels = analyzeOrigin(nodes["parameters"]["param"]["paramLine"]["param"][0]["string"])
                    workSheetParam.write(index, 1, listOfModels["DS"])
                    workSheetParam.write(index, 2, listOfModels["DE"])
                    workSheetParam.write(index, 3, listOfModels["DM"])
                    workSheetParam.write(index, 4, nodes["parameters"]["param"]["paramLine"]["param"][0]["string"])
                    workSheetParam.write(index, 5, nodes["parameters"]["param"]["paramLine"]["param"][1]["string"])
                    workSheetParam.write(index, 6, " ".join(getDependencies(nodes["parameters"]["param"]["paramLine"]["param"][1]["string"])[0]))
                    workSheetParam.write(index, 7, " ".join(getVariableOrigin(nodes["parameters"]["param"]["paramLine"]["param"][1]["string"])))
                    workSheetParam.write(index, 8, " ".join(getDependencies(nodes["parameters"]["param"]["paramLine"]["param"][1]["string"])[1]))
                    #CheckValueInReport
                    getValuesOfVariables(nodes["_name"], " ".join(getDependencies(nodes["parameters"]["param"]["paramLine"]["param"][1]["string"])[1]))
                indexSheet = 9
                for inform in jsonArchives:
                    workSheetParam.write_formula(index, indexSheet, "=VLOOKUP(A" + str(index + 1) + "," + inform.split(".")[0] + "!C:C,1,FALSE())")
                    indexSheet = indexSheet + 1
                index = index +1
            workSheetParam.autofilter(0, 0, index, (8 + len(jsonArchives)))
            setColumnsWidth(workSheetParam)
            return varExpression        


        def checkCondition(condition, columns, numberOfValue):
            global formula
            global i
            isNot = False
            if isinstance(condition, str):
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
                if(len(condition) == 1):
                    if(isinstance(columns["COPULA"], list)):
                        enterValue(isNot, condition["CONDITION"], columns["COPULA"][numberOfValue])
                    else:
                        enterValue(isNot, condition["CONDITION"], columns["COPULA"])
                #Involves more than one Condition
                else:  
                    if(isinstance(columns["COPULA"], list)):
                        enterValue(isNot, condition, columns["COPULA"][numberOfValue])
                    else:
                        enterValue(isNot, condition, columns["COPULA"])
            #Last Condition
            else:
                if (len(condition) == 1):
                    enterValue(isNot, condition["CONDITION"], "")
                else:
                    enterValue(isNot, condition, "")
            numberOfValue = numberOfValue + 1
            return numberOfValue
        
        def enterColumn(isNot, listOfValues, listOfCopulas):
            global valuesTaken
            global formula
            global i
            global origin
            valorVar = ""
            valuesTaken = ""
            if listOfValues["_type"] != "EXPRESSION_FREEHAND":
                if isinstance(listOfValues["COLUMN"], list):
                    for column in listOfValues["COLUMN"]:
                        valorVar = valorVar + " " + column["COLNAME"]
                        #Añadir al diccionario de variables
                        if not(column["COLNAME"] in axiomVarReport):
                            axiomVarReport[column["COLNAME"]] = ""
                else:
                    valorVar = listOfValues["COLUMN"]["COLNAME"]
                    #Añadir al diccionario de variables
                    if not(listOfValues["COLUMN"]["COLNAME"]in axiomVarReport):
                        axiomVarReport[listOfValues["COLUMN"]["COLNAME"]] = ""

                if isinstance(listOfValues["VALUE"], list):
                    definition = []
                    index = 0
                    if (listOfValues["_type"] == "DATE_INTERVAL_REGULAR"):
                        definition = [" year ", " month ", " day "]
                    def_iterator = iter(definition)
                    for values in listOfValues["VALUE"]:
                        valuesTaken = valuesTaken + " " + str(values) + next(def_iterator, "")
                        index = index + 1
                else:
                    valuesTaken = listOfValues["VALUE"]
            #Enter formula en formula attribute
            formula = formula + "(" + valorVar + " " + listOfValues["OPERATION"] + " " + valuesTaken + ")"
            if(listOfCopulas != ""):
                formula = formula + " " + listOfCopulas + " " 
            worksheet.write(i, 0, registers[j])
            worksheet.write(i, 1, origin)
            #worksheet.write(i, 1, listOfCopulas)
            worksheet.write(i, 2, valorVar)
            worksheet.write(i, 3, ("", "NOT ")[isNot] + listOfValues["OPERATION"].replace("<=","minor or equal").replace('=', " equal"))
            worksheet.write(i, 4, valuesTaken)

            i = i + 1
            
        def enterValue(isNot, listOfValues, listOfCopulas):
            global formula
            global cuenta
            global i
            global valuesTaken
            global origin
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
                i = mappingAttributes(i, 5, valuesTaken, worksheet, registers[j], origin)
            else:
                enterColumn(isNot, listOfValues, listOfCopulas)
                i = mappingAttributes(i, 5, valuesTaken, worksheet, registers[j], origin)

        #Get Registers from Nodes
        registers = []
        registersFromNode = []
        getRegistersForNodes("archives/" + informName + "_nodes" + ".json")
        registers = registersFromNode
        print(len(registers))
        #Get all the condition for each Register
        index = 0
        i = 1
        j = 0
        for columns in jsoncolumnspy["JSONCOLUMNS"]["CONDITION"]:
            #print("index: " + str(index))
            index = i
            if (getOrigin(registers[j]) != ""):
                origin = getOrigin(registers[j])
            if bool(columns):
                worksheet.write(i, 0, registers[j])
                worksheet.write(i, 1, origin)
                numberOfValue = 0
                formula = ""
                #Only one Condition a list
                if (len(columns["CONDITION"]) ==  1):
                    isNot = False
                    if(len(columns) == 2):
                        isNot = True
                        formula = " NOT("
                    enterValue(isNot, columns["CONDITION"]["CONDITION"], "")
                #Only One condition and not a list
                elif (not(isinstance(columns["CONDITION"], list)) and (len(columns["CONDITION"].keys()) > 2)):
                    isNot = False
                    if(len(columns) == 2):
                        isNot = True
                        formula = " NOT("
                    enterValue(isNot, columns["CONDITION"], "")                   
                else:
                    #Get all the conditions for each previous condition
                    if isinstance(columns["CONDITION"], list):
                        for condition in columns["CONDITION"]:
                            numberOfValue = checkCondition(condition, columns, numberOfValue)
                            #i = i + 1
                    else:
                        for condition in columns["CONDITION"]["CONDITION"]:
                            numberOfValue = checkCondition(condition, columns["CONDITION"], numberOfValue)
                print(str(j) + ":" + str(registers[j]))
            else:
                worksheet.write(i, 0, registers[j])
                worksheet.write(i, 1, origin)
                print("Empty " + str(j) + ": " + str(registers[j]))
                i = i+1
            j = j + 1
            worksheet.write(index, 11, formula)
        #Save Variables of Axiom in Dictionary
        axiomVar[informName] = axiomVarReport
        axiomVarReport = {}
        worksheet.autofilter(0, 0, i, 11)
        #Change Width
        width = 5
        worksheet.set_column(0, 1, 3*width)
        worksheet.set_column(7, 7, 3*width)
        worksheet.set_column(9, 9, 3*width)
        worksheet.set_column(5, 5, 4*width)
        worksheet.set_column(6, 6, 5*width)
        worksheet.set_column(2, 2, 5*width)
        worksheet.set_column(3, 3, 3*width)
        worksheet.set_column(8, 8, 3*width)
        worksheet.set_column(4, 4, 8*width)
        worksheet.set_column(11, 11, 20*width)
        

for aggregationName in aggregationNames:
    print(aggregationName)
    workSheetAggregation = newAggregationSheet(aggregationName)
    with open("FinstatAggregation/Aggregation" + aggregationName + ".json") as jsonAggregation:
        jsonAggregationpy = json.load(jsonAggregation)
        enterAggregation(jsonAggregationpy, workSheetAggregation)

def createSheetWithVars():
    worksheetVar = workbook.add_worksheet("Relación reporte variables")
    worksheetVar.write(0, 1, "Reporte", header_format)
    worksheetVar.write(0, 2, "Variable Axiom", header_format)
    worksheetVar.write(0, 3, "Variables DS", header_format)
    worksheetVar.write(0, 4, "Tabla", header_format)
    worksheetVar.write(0, 5, "Perímetro", header_format)
    worksheetVar.write(0, 6, "Transformación Direct Mapping", header_format)
    worksheetVar.write(0, 7, "Comprobación Reporting", header_format)
    worksheetVar.write(0, 8, "Comentarios", header_format)
    worksheetVar.freeze_panes(1, 1)
    return worksheetVar

def fillSheetVar(worksheetVar):
    print(axiomVar)
    index = 1
    for key in axiomVar.keys():
        for var in axiomVar[key].keys():
            worksheetVar.write(index, 1, key)
            worksheetVar.write(index, 2, var)
            worksheetVar.write(index, 3, axiomVar[key][var])
            index = index + 1  

fillSheetVar(createSheetWithVars())
workbook.close()