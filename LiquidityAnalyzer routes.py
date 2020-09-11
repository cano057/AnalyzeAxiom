import xlsxwriter
import json
from pathlib import Path
from PortfolioConversion import PortfolioConversion
#Se analizan los diferentes informes de Liquidez de Axiom, los filtros que hace cada rúbrica y el origen de las variables usadas.
#Origen: 1) Mapeo: Portfolios de DirectMapping con una estructura dividida en esquema y condiciones (json)
#        2) Conversión: Agregaciones con variables creadas a partir de otras variables, misma estructura que el anterior (json)

#Variables Globales
i = 2
j =0
#Registros nodos
registers = []
aggregationNames = ["Position", "Cashflow"]
origin = ""

#Listado de Variables obtenidas {Variable en Axiom : Variable origen}
axiomVar = {}
axiomVarReport = {}

#Listado de Diccionarios Maping
portfolioConversion = PortfolioConversion()
mappingConversion = PortfolioConversion()
calcConversion = PortfolioConversion()
mappingDictionaries = mappingConversion.convertPortfolio("mapping")

#Listado de Diccionarios de Conversiones
portfDictionaries = portfolioConversion.convertPortfolio("archives") 

#Listado de Diccionarios de Cálculos
calcDictionaries = calcConversion.convertPortfolioActions("calc")
        

def modifyFormat(stringValue, formatValue):
    if(((stringValue[(len(stringValue)- len(formatValue)) :]) != formatValue) or ((len(stringValue)- len(formatValue)) <= 0)):
        print (stringValue + formatValue)
        return (stringValue + formatValue)
    else:
        print ("correct format")
        return stringValue

workbookName = input("Tecle el nombre del archivo xlsx de salida \n")
workbookName = modifyFormat(workbookName, ".xls")

valuesTaken = ""
formula = ""

#workSheet Reporte
workbook = xlsxwriter.Workbook(workbookName)
xlsxwriter.Workbook(workbook, {'strings_to_numbers' : False , 'strings_to_formulas' : True , 'strings_to_urls' : True})
header_format = workbook.add_format({'bold': True,'border': 6,'align': 'center','valign': 'vcenter','fg_color': '#999999'})


def createWorkSheet(workSheetName):
    worksheet = workbook.add_worksheet(workSheetName)

    worksheet.write(0, 0, "register name", header_format)
    #worksheet.write(1, 1, "Yes or Not")
    worksheet.write(0, 1, "Parent", header_format)
    worksheet.write(0, 2, "Formula", header_format)
    worksheet.write(0, 3, "varOrigin", header_format)
    worksheet.write(0, 4, "var", header_format)
    worksheet.write(0, 5, "operator", header_format)
    worksheet.write(0, 6, "value", header_format)
    worksheet.write(0, 7, "Alias", header_format)
    worksheet.write(0, 8, "Colname", header_format)
    worksheet.write(0, 9, "Operation", header_format)
    worksheet.write(0, 10, "Value", header_format)
    worksheet.freeze_panes(1, 1)

    return worksheet

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
    for inform in portfDictionaries:
        workAggregationSheet.write(0, indexSheet, "Está en " + inform["name"], header_format) 
        indexSheet = indexSheet + 1
    workAggregationSheet.freeze_panes(1, 1)
    return workAggregationSheet

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
    
#Change the Columns Width
def setColumnsWidth(workSheetParam):
    width = 5
    workSheetParam.set_column(0, 0, 5*width)
    workSheetParam.set_column(1, 3, 10*width)
    workSheetParam.set_column(4, 5, 20*width)

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

def searchConditionDependency(register, value):
    for condition in register["conditions"]:
        for var in condition["var"]:
            if(var == value):
                return condition
                break
    return ""

def searchDependency(registers, value):
    conditions = []
    for register in registers:
        if(isinstance(searchConditionDependency(register, value), dict)):
            conditions.append(searchConditionDependency(register, value))     
    if (register["registers"]):
        if(searchDependency(register["registers"], value)):
            for condition in searchDependency(register["registers"], value):
                conditions.append(condition)
        return [d["values"] for d in conditions]
    else:
        return conditions

def getDependenciesOfCalc(value, aggregationName):
    dependencies = []
    for portfolio in calcDictionaries:
        if(portfolio["name"] == aggregationName[1:-1]):
            if (searchDependency(portfolio["registers"], value)):
                dependencies = searchDependency(portfolio["registers"], value)
                break
    if(dependencies):
        if(isinstance(dependencies[0], dict)):
            return [d["values"] for d in dependencies]
    return dependencies

def searchValueInReport(report, value):
    for key in report.keys():
        for dependency in report[key]["dependencies"]:
            if(value == dependency):
                return report[key]["parent"]
    return []

def isValueInReport(report, value, aggregationName):
    for key in report.keys():
        index = 0
        for dependency in report[key]["dependencies"]:
            if(value == dependency):
                if(report[key]["models"][index].split("_")[0].lower() == aggregationName.lower()):
                    return True
            index = index + 1
    return False

def getValuesOfVariables(report, value, valueModels, valueOrigin, aggregationName):
    if (value in report.keys()):
        if (not report[value]["dependencies"]):
            report[value]["models"] = valueModels
            if(isinstance(valueOrigin, dict)):
                report[value]["dependencies"] = [d['value'] for d in valueOrigin]
            else:
                report[value]["dependencies"] = [valueOrigin]
    elif (isValueInReport(report, value, aggregationName)):
        for n, dependency in enumerate(valueModels):
            calcPortfolio = (dependency.split("$Portfolio"))
            if(len(calcPortfolio) > 1):
                dependencyCalc = getDependenciesOfCalc(value, calcPortfolio[1])
                valueModels[n] = ""
                for d in dependencyCalc:
                    valueModels[n] = " ".join((valueModels[n],(" ".join(d))))
        report[aggregationName + " " + value] = {"models" : valueModels, "dependencies" : valueOrigin, "parent" : searchValueInReport(report, value)}


#Enter all the Origin and Expressions for the differents attributes in an Aggregation
def enterAggregation(jsonArchive, workSheetParam, aggregationName):
    global axiomVarReport
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
                dependencies = getDependencies(paramLine["param"][1]["string"])
                for key in axiomVar.keys():
                    getValuesOfVariables(axiomVar[key], nodes["_name"], dependencies[0], dependencies[1], aggregationName)
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
            dependencies = getDependencies(nodes["parameters"]["param"]["paramLine"]["param"][1]["string"])
            for key in axiomVar.keys():
                getValuesOfVariables(axiomVar[key], nodes["_name"], dependencies[0], dependencies[1], aggregationName)
        indexSheet = 9
        for inform in portfDictionaries:
            workSheetParam.write_formula(index, indexSheet, "=IF.ERROR(VLOOKUP(A" + str(index + 1) + "," + inform["name"]+ "!C:C,1,FALSE()),VLOOKUP(A" + str(index + 1) + "," + inform["name"]+ "!I:I,1,FALSE())")
            indexSheet = indexSheet + 1
        index = index +1
    workSheetParam.autofilter(0, 0, index, (8 + len(portfDictionaries)))
    setColumnsWidth(workSheetParam)
    return varExpression        

def setReportColumnsWidth(workSheetParam, width):
    workSheetParam.set_column(0, 1, 3*width) 
    workSheetParam.set_column(2, 2, 8*width)
    workSheetParam.set_column(3, 3, 5*width)
    workSheetParam.set_column(4, 4, 8*width)
    workSheetParam.set_column(5, 5, 4*width)
    workSheetParam.set_column(6, 6, 8*width)
    workSheetParam.set_column(7, 7, 5*width)
    workSheetParam.set_column(8, 8, 8*width)
    workSheetParam.set_column(9, 9, 3*width)
    workSheetParam.set_column(10, 10, 8*width)

def getVarFromList(listParam):
    listResult = []
    for element in listParam:
        for var in element["var"]:
            listResult.append(var["name"])
    return list(dict.fromkeys(listResult))

def checkValueRepeated(report, value, condition):
    index = 0
    for dependency in report[value]["dependencies"]:
        if (condition["name"] == dependency):
            if(report[value]["models"][index] == condition["alias"]):
                return False
        index = index + 1
    return True

def getConditions(registers, value, parent):
    conditions = []
    for register in registers["registers"]:
        if(parent[0] == register["name"]):
            if(parent[0] == value):
                conditions = register["conditions"]
                break
            else:
                if(register["registers"]):
                    conditions = getConditions(register, value, parent[1:])
                    break
    return conditions

def searchValues(portfolio, value, parent):
    global axiomVarReport
    conditions = []
    for register in portfolio["registers"]:
        if(getConditions(register, value, parent)):
            conditions = getConditions(register, value, parent)
            break
    return conditions

def paintOriginOfValues(portfWorkSheet, value, model, parent, name, origin, index):
    global axiomVarReport
    i = index
    conditions = []
    for portfolio in mappingDictionaries:
        if(searchValues(portfolio, value, parent)):
            conditions = searchValues(portfolio, value, parent)
            break
    for condition in conditions:
        for cvar in condition["var"]:
            if(value in axiomVarReport.keys()):
                if(checkValueRepeated(axiomVarReport, value, cvar)):
                    axiomVarReport[value]["models"].append(cvar["alias"])
                    if(len(cvar["name"].split("ref_")) > 1):
                        axiomVarReport[value]["dependencies"].append(cvar["name"].split("ref_")[1])
                    else:
                        axiomVarReport[value]["dependencies"].append(cvar["name"])
                    axiomVarReport[value]["subdependencies"] = []
            portfWorkSheet.write(i + condition["var"].index(cvar), 7, cvar["alias"])
            portfWorkSheet.write(i + condition["var"].index(cvar), 8, cvar["name"])
        portfWorkSheet.write(i, 9, condition["operator"].replace("<=","minor or equal").replace('=', " equal"))
        for cvalue in condition["values"]:
            portfWorkSheet.write(i, 0, name)
            portfWorkSheet.write(i, 1, origin)  
            portfWorkSheet.write(i + condition["values"].index(cvalue), 10, cvalue)
        i = i + len(condition["values"])
    return i


def paintRegistersOfPortf(portfWorksheet, registers, origin, index):
    i = index
    for register in registers:
        print(register["name"])
        portfWorksheet.write(i, 0, register["name"])
        portfWorksheet.write(i, 1, origin)
        #Paint conditions of register
        if(len(register["conditions"]) > 0):
            portfWorksheet.write(i, 2, register["formula"])
            for condition in register["conditions"]:
                for var in condition["var"]:
                    portfWorksheet.write(i + condition["var"].index(var), 3, var["alias"])
                    portfWorksheet.write(i + condition["var"].index(var), 4, var["name"])
                portfWorksheet.write(i, 5, condition["operator"].replace("<=","minor or equal").replace('=', " equal"))
                for value in condition["values"]:
                    portfWorksheet.write(i, 0, register["name"])
                    portfWorksheet.write(i, 1, origin)
                    portfWorksheet.write(i, 6, value)
                    #Save value if it does not exist
                    parent = []
                    if(value.split("/") and (value[-1] == "/")):
                        valueSplitted = value.split("/")[-2]
                    else:
                        valueSplitted = value
                    parent = [item for item in value.split("/") if item]
                    if condition["values"]:
                        if(not(valueSplitted in axiomVarReport.keys())):
                            axiomVarReport[valueSplitted] = {"models" : [], "dependencies" : [], "parent": parent}
                        iprevious = i
                        i = paintOriginOfValues(portfWorksheet, valueSplitted, register["models"], axiomVarReport[valueSplitted]["parent"], register["name"], origin ,i)
                    else:
                        i = i + 1
        else:
            i = i + 1
        if(len(register["registers"]) > 0):
            paintRegistersOfPortf(portfWorksheet, register["registers"], register["name"], i)
    return index

def getModelFromAgg(model):
    switcher = {"position": "PositionCalc_Input", "position_ref_position": "PositionCalc_Input", "cashflow": "CashflowCalc_Input", "cashflow_ref_position": "CashflowCalc_Input", "counterparty": "CounterpartyCalc_Input", }
    modelResult = switcher.get(model, model)
    return modelResult

#Get all the condition for each Register (Portfolio Reporting) and compare it with Mapping Portfolio
index = 1
for portfolio in portfDictionaries:
    worksheet = createWorkSheet(portfolio["name"])
    index = paintRegistersOfPortf(worksheet, portfolio["registers"], portfolio["name"], index)
    axiomVar[portfolio["name"]] = axiomVarReport.copy()
    axiomVarReport = {}
    worksheet.autofilter(0, 0, index, 11)
    #Change Width
    setReportColumnsWidth(worksheet, 5)

#Get dependencies from Aggregations and Calc_Input
for aggregationName in aggregationNames:
    print(aggregationName)
    workSheetAggregation = newAggregationSheet(aggregationName)
    with open("LiquidityAggregations/Aggregation" + aggregationName + ".json") as jsonAggregation:
        jsonAggregationpy = json.load(jsonAggregation)
        enterAggregation(jsonAggregationpy, workSheetAggregation, aggregationName)

for key in axiomVar.keys():
    for var in axiomVar[key].keys():
        index = 0
        model = ""
        for dependency in axiomVar[key][var]["dependencies"]:
            model = getModelFromAgg(axiomVar[key][var]["models"][index])
            axiomVar[key][var]["subdependencies"] = getDependenciesOfCalc(dependency, model)
            #print(axiomVar[key][var]["subdependencies"])
            index = index + 1

def createSheetWithVars():
    worksheetVar = workbook.add_worksheet("Relación reporte variables")
    worksheetVar.write(0, 0, "Reporte", header_format)
    worksheetVar.write(0, 1, "Variable Axiom", header_format)
    worksheetVar.write(0, 2, "Ruta", header_format)
    worksheetVar.write(0, 3, "Variables DS", header_format)
    worksheetVar.write(0, 4, "Tabla", header_format)
    worksheetVar.write(0, 5, "Perímetro", header_format)
    worksheetVar.write(0, 6, "Transformación Direct Mapping", header_format)
    worksheetVar.write(0, 7, "Comprobación Reporting", header_format)
    worksheetVar.write(0, 8, "Comentarios", header_format)
    worksheetVar.freeze_panes(1, 1)
    return worksheetVar

def fillSheetVar(worksheetVar):
    index = 1
    for key in axiomVar.keys():
        for var in axiomVar[key].keys():
            worksheetVar.write(index, 0, key)
            worksheetVar.write(index, 1, var)
            worksheetVar.write(index, 2, "/".join(axiomVar[key][var]["parent"]))
            i = 0
            for dependency in axiomVar[key][var]["dependencies"]:
                worksheetVar.write(index, 3, dependency)
                worksheetVar.write(index, 4, axiomVar[key][var]["models"][i])
                if(len(axiomVar[key][var]["subdependencies"]) > i):
                    worksheetVar.write(index, 4, axiomVar[key][var]["subdependencies"][i])
                i = i + 1
                index = index + 1

fillSheetVar(createSheetWithVars())
workbook.close()