import xlsxwriter
import json

i = 1
j =0
registros01 = ["F_01_01", "position", "300", "current_assets", "010", "030", "040", "050", "060", "070", "080", "090", "096", "097", "098", "099", "100", "120", "130", "141", "142", "143", "144", "181", "182", "183", "240", "250", "260", "360", "370", "OAL", "380", "Current_assets", "010", "20", "260", "270", "280", "290", "300", "310", "320", "330", "340", "350", "370", "360"]
registros02 = ["F_01_02", "position", "300", "current_assets", "010", "020", "030", "040", "050", "060", "070", "080", "090", "100", "110", "120", "130", "140", "150", "160", "280", "290", "OAL", "300", "Current_assets", "170","180", "190", "200", "210", "220", "230", "240", "250", "260", "270", "280", "290"]
registros03 = ["F_01_03", "300", "current_assets", "010", "030", "020", "040", "050", "060", "070", "080", "090", "095", "100", "110", "120", "124", "320", "128", "130", "140", "150", "155", "165", "180", "190", "200", "210", "220", "230", "240", "250", "260", "270", "280", "290", "non current_assets", "122", "170", "330", "340", "350", "360"]
registros0901 = ["F09_01_01", "010", "030", "021", "Others", "040", "021", "Others", "050", "021", "Others", "060", "021", "Others", "070", "021", "Others", "080", "021", "Others", "090", "110", "101", "Others", "120", "101", "Others", "130", "101", "Others", "140", "101", "Others", "150", "101", "Others", "160", "101", "Others", "170", "190", "181", "Others", "200", "181", "Others", "210", "181", "Others", "220", "181", "Others", "230", "181", "Others", "240", "181", "Others"]
registros0902 = ["F09_02", "010", "020", "030", "040", "050","060", "070", "080", "090","100", "110", "120", "130", "140", "150", "160", "170", "180", "190", "200", "210"]
registers = registros0902
origin = ""
#origin = {}

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

def modifyFormat(stringValue, formatValue):
    if(((stringValue[(len(stringValue)- len(formatValue)) :]) != formatValue) or ((len(stringValue)- len(formatValue)) <= 0)):
        print (stringValue + formatValue)
        return (stringValue + formatValue)
    else:
        print ("correct format")
        return stringValue

jsonArchive = input("Teclee el nombre del archivo JSON que contenga los filtros \n")
jsonArchive = modifyFormat(jsonArchive, ".json")
jsonArchiveNodesRegister = jsonArchive.split(".")[0] + "_nodes" + ".json"
jsonArchiveNodes = input("Teclee el nombre del archivo JSON que contenga los nodos \n")
jsonArchiveNodes = modifyFormat(jsonArchiveNodes, ".json")
jsonArchivePosition = "PositionAggregation.json"
jsonArchiveOAL = "OALAggregation.json"
workbookName = input("Tecle el nombre del archivo xlsx de salida \n")
workbookName = modifyFormat(workbookName, ".xls")

valuesTaken = ""
cuenta = 0
formula = ""
#Portfolio JSON
filterDicc = {"Tipo" : "", "Alias" : "", "Colname" : "", "Operation" : "", "Valor" : "", "Copula" : ""}
filterList = []
conditionDicc ={"Variable" : "", "Operacion" : "", "Valor" : "", "Filtros" : []}
conditionList = []
registerDicc = {"Nombre" : "", "Origen" : "", "Condiciones" : [], "Formula" : ""}
registerList = []

with open(jsonArchiveNodes) as jsonNodes:
    jsonNodespy = json.load(jsonNodes)
    with open(jsonArchive) as jsoncolumns:
        jsoncolumnspy = json.load(jsoncolumns)

        #workSheet Reporte
        workbook = xlsxwriter.Workbook(workbookName)
        xlsxwriter.Workbook(workbook, {'strings_to_numbers' : False , 'strings_to_formulas' : True , 'strings_to_urls' : True})
        header_format = workbook.add_format({'bold': True,'border': 6,'align': 'center','valign': 'vcenter','fg_color': '#999999'})
        worksheet = workbook.add_worksheet(registers[j])

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


        #workSheet Position
        worksheetPos = workbook.add_worksheet("Position")
        worksheetPos.write(0, 0, "Variable", header_format)
        worksheetPos.write(0, 1, "Data Staging", header_format)
        worksheetPos.write(0, 2, "Data Enrichment", header_format)
        worksheetPos.write(0, 3, "Direct Mapping", header_format)
        worksheetPos.write(0, 4, "Origen", header_format)
        worksheetPos.write(0, 5, "Expression", header_format)
        worksheetPos.freeze_panes(1, 1)


        #WorkSheet OAL
        worksheetOAL = workbook.add_worksheet("OAL")
        worksheetOAL.write(0, 0, "Variable", header_format)
        worksheetOAL.write(0, 1, "Data Staging", header_format)
        worksheetOAL.write(0, 2, "Data Enrichment", header_format)
        worksheetOAL.write(0, 3, "Direct Mapping", header_format)
        worksheetOAL.write(0, 4, "Origen", header_format)
        worksheetOAL.write(0, 5, "Expression", header_format)
        worksheetOAL.freeze_panes(1, 1)

        def initiateRegister():
            global registerDicc
            registerDicc.clear()
            registerDicc = {"Nombre" : "", "Origen" : "", "Condiciones" : [], "Formula" : ""}
        
        def initiateCondition():
            global conditionDicc
            conditionDicc.clear()
            conditionDicc ={"Variable" : "", "Operacion" : "", "Valor" : "", "Filtros" : []}

        def getValues(listOfValues):
            valorVar = ""
            if listOfValues["_type"] != "EXPRESSION_FREEHAND":
                if isinstance(listOfValues["COLUMN"], list):
                    for column in listOfValues["COLUMN"]:
                        valorVar = valorVar + " " + column["COLNAME"]
                else:
                    valorVar = listOfValues["COLUMN"]["COLNAME"]
            else:
                valorVar = 
            return valorVar

        def enterCondition(isNot):
            global conditionDicc
            initiateCondition()
            global valuesTaken
            global formula
            
            valorVar = ""
            valuesTaken = ""
            if listOfValues["_type"] != "EXPRESSION_FREEHAND":
                if isinstance(listOfValues["COLUMN"], list):
                    for column in listOfValues["COLUMN"]:
                        valorVar = valorVar + " " + column["COLNAME"]
                else:
                    valorVar = listOfValues["COLUMN"]["COLNAME"]

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
            #Enter formula in formula attribute
            formula = formula + "(" + valorVar + " " + listOfValues["OPERATION"] + " " + valuesTaken + ")"
            if(listOfCopulas != ""):
                formula = formula + " " + listOfCopulas + " " 
            conditionDicc["Variable"] = valorVar
            conditionDicc["Operacion"] = ("", "NOT ")[isNot] + listOfValues["OPERATION"].replace("<=","minor or equal").replace('=', " equal")
            conditionDicc["Valor"] = valuesTaken

        def getConditions():

        #Get all the condition for each Register
        def getRegisters():
            global formula
            global registroDicc
            global registroList
            index = 0
            for columns in jsoncolumnspy["JSONCOLUMNS"]["CONDITION"]:
                initiateRegister()
                index = i
                formula = ""
                registroDicc["Nombre"] = registers[j]
                if (getOrigin(registers[j]) != ""):
                    registroDicc["Origin"] = getOrigin(registers[j])
                if bool(columns):
                    numberOfValue = 0
                    #Only one Condition
                    if (len(columns["CONDITION"]) ==  1):
                        isNot = False
                        if(len(columns) == 2):
                            isNot = True
                            formula = " NOT("
                        enterCondition(isNot, columns["CONDITION"]["CONDITION"], "")
                    else:
                        #Get all the conditions for each previous condition
                        if isinstance(columns["CONDITION"], list):
                            for condition in columns["CONDITION"]:
                                numberOfValue = getConditions(condition, columns, numberOfValue)
                        else:
                            for condition in columns["CONDITION"]["CONDITION"]:
                                numberOfValue = getConditions(condition, columns["CONDITION"], numberOfValue)
                    print(str(j) + ":" + str(registers[j]))
                else:
                    worksheet.write(i, 0, registers[j])
                    worksheet.write(i, 1, origin)

                    print("Empty " + str(j) + ": " + str(registers[j]))
                    i = i+1
                j = j + 1
                registroDicc["Formula"] = formula
                registroList.append(registroDicc)

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
            

        def mappingAttributes(index, firsPosition, valuesTakenParam, workSheetParam, variable, origin):
            indexn = index
            with open(jsonArchiveNodes) as jsonNodes:
                jsonNodespy = json.load(jsonNodes)
                for portfolios in jsonNodespy["nodes"]["portfolio-node"]:
                    for node in portfolios["portfolio-node"]:
                        #print(valuesTakenParam + " = " + node["_name"])
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

        #Enter all the Origin and Expressions for the differents attributes in an Aggregation
        def enterAggregation(jsonArchive, workSheetParam):
            varExpression = ""
            varName = ""
            index = 1
            listOfModels = {}
            for nodes in jsonArchive["nodes"]["parameterNode"]["parameterNode"][1]["parameterNode"]:
                workSheetParam.write(index, 0, nodes["_name"])
                listOfModels = analyzeOrigin(nodes["parameters"]["param"]["paramLine"]["param"][0]["string"])
                workSheetParam.write(index, 1, listOfModels["DS"])
                workSheetParam.write(index, 2, listOfModels["DE"])
                workSheetParam.write(index, 3, listOfModels["DM"])
                workSheetParam.write(index, 4, nodes["parameters"]["param"]["paramLine"]["param"][0]["string"])
                workSheetParam.write(index, 5, nodes["parameters"]["param"]["paramLine"]["param"][1]["string"])
                index = index + 1
            workSheetParam.autofilter(0, 0, index, 5)
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
                else:
                    valorVar = listOfValues["COLUMN"]["COLNAME"]

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
            else:
                enterColumn(isNot, listOfValues, listOfCopulas)
                i = mappingAttributes(i, 5, valuesTaken, worksheet, registers[j], origin)
        #Get all the condition for each Register
        index = 0
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
                #Only one Condition
                if (len(columns["CONDITION"]) ==  1):
                    isNot = False
                    if(len(columns) == 2):
                        isNot = True
                        formula = " NOT("
                    enterValue(isNot, columns["CONDITION"]["CONDITION"], "")
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

        #Get Aggregation Variables
        with open(jsonArchivePosition) as jsonPosition:
            jsonPositionpy = json.load(jsonPosition)
            enterAggregation(jsonPositionpy, worksheetPos)
        with open(jsonArchiveOAL) as jsonOAL:
            jsonOALpy = json.load(jsonOAL)
            enterAggregation(jsonOALpy, worksheetOAL)
       
        #print(cuenta)


        workbook.close()