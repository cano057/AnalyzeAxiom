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
aggregationNames = ["CR_SA_Capital_Requirements_Pre", "CR_Exposure_Calc_Inputs"]
origin = ""

#Listado de Variables obtenidas {Variable en Axiom : Variable origen}
axiomVar = {}
axiomVarReport = {}

#Listado de Diccionarios Maping
#portfolioConversion = PortfolioConversion()
#mappingConversion = PortfolioConversion()
calcConversion = PortfolioConversion()
#mappingDictionaries = mappingConversion.convertPortfolio("mapping")

#Listado de Diccionarios de Conversiones
#portfDictionaries = portfolioConversion.convertPortfolio("archives") 

#Listado de Diccionarios de Cálculos
calcDictionaries = calcConversion.convertPortfolioActions("calc")
modelAggParams = {"Aggregation" : "AggCR_Exposure_Calc_Inputs", "eu_cr_exposure" : "AggEU_CR_Exposure_Calc_Inputs", "guarantor_party" : "AggRef_Party", "entity_hierarchy" : "AggRef_Reporting_Entity_Hierarchy", "entity" : "AggRef_Reporting_Entity", "fx_rate" : "AggRef_FX_Rate", "eu_entity" : "AggEU_Ref_Reporting_Entity", "fx_rate_eu_entity" : "AggRef_FX_Rate", "eu_intra_group_type" : "AggEU_Ref_Intra_Group_Type", "eu_other_retail" : "AggEU_Other_Retail_Amounts_Owed", "eur_fx__rate" : "AggRef_FX_Rate", "ccp_counterparty" : "AggRef_CCP", "fx_rate_ccp" : "AggRef_FX_Rate", "counterparty" : "AggRef_Party", "eu_counterparty" : "AggEU_Ref_Party", "third_country" : "Third_Country_Check", "fx_rate_counterparty" : "AggRef_FX_Rate", "central_government" : "AggRef_Party", "entity_counterparty" : "AggRef_Reporting_Entity_Hierarchy", "issuer" : "AggRef_Party", "CPARTY_TYPE" : ""}
modelPreAggParams = {"Aggregation" : "AggCR_Exposure_Calc_Inputs", "relevant_credit_exposure" : "AggRelevant_Credit_Exposure", "ref_sec_report_data" : "AggEU_Ref_SEC_Report_Data"}        

def modifyFormat(stringValue, formatValue):
    if(((stringValue[(len(stringValue)- len(formatValue)) :]) != formatValue) or ((len(stringValue)- len(formatValue)) <= 0)):
        print (stringValue + formatValue)
        return (stringValue + formatValue)
    else:
        print ("correct format")
        return stringValue

#Archives
def ls3(path):
    return [obj.name for obj in Path(path).iterdir() if obj.is_file()]

def getJSON(folderJSON):
        archivesFiles=ls3(folderJSON) 
        jsonArchives = []
        for file in archivesFiles:
            if(len(file.split("_nodes")) == 1):
                jsonArchives.append(file)
                print(file)
        return jsonArchives

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
            origin = expression[pos:].split(".")[0][1:]
            if(len(variable.split(" ")[0]) > 1):
                variable = variable.split(" ")[0]
                if(variable[-1] == ","):
                    variable = variable[0:-1]
                if(variable.find('=') >= 0):
                    variable = variable.split('=')[0]
            dependencies.append(variable)
            origins.append(origin)
        pos = expression.find('$', pos+1, len(expression))
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

def getDependenciesOfCalc(value):
    dependencies = []
    for portfolio in calcDictionaries:
        dependencies = searchDependency(portfolio["registers"], value)
        if(dependencies):
            if(isinstance(dependencies[0], dict)):
                return [d["values"] for d in dependencies]
            if(isinstance(dependencies[0], list)):
                newd = []
                for dependency in dependencies:
                    for d in dependency:
                        newd.append(d)
                return newd
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

def getValuesOfVariables(value, valueModels, valueOrigin, valueParent):
    global axiomVarReport
    if (value in axiomVarReport.keys()):
        for model in axiomVarReport[value]["models"]:
            if (model == valueModels):
                #pendiente juntar las listas
                if(isinstance(valueOrigin, dict)):
                    axiomVarReport[value]["dependencies"].extend([d['value'] for d in valueOrigin])
                else:
                    axiomVarReport[value]["dependencies"].extend(valueOrigin)
                if(isinstance(valueParent, dict)):
                    axiomVarReport[value]["dependencies"].extend([d['value'] for d in valueParent])
                else:
                    axiomVarReport[value]["parent"].extend(valueParent)
    else:
        axiomVarReport[value] = {"models" : [valueModels], "dependencies" : valueOrigin, "parent" : valueParent}

#Analyze all the nodes into a ParameterNode variable
def analyzeParameterNode(workSheetParam, nodes, nodesName, index, aggregationName, getVar):
    global axiomVarReport
    workSheetParam.write(index, 0, nodesName)
    listOfModels = analyzeOrigin(nodes["param"][0]["string"])
    workSheetParam.write(index, 1, listOfModels["DS"])
    workSheetParam.write(index, 2, listOfModels["DE"])
    workSheetParam.write(index, 3, listOfModels["DM"])
    workSheetParam.write(index, 4, nodes["param"][0]["string"])
    workSheetParam.write(index, 5, nodes["param"][1]["string"])
    dependencies = getDependencies(nodes["param"][1]["string"])
    workSheetParam.write(index, 6, " ".join(dependencies[0]))
    workSheetParam.write(index, 7, " ".join(getVariableOrigin(nodes["param"][1]["string"])))
    workSheetParam.write(index, 8, " ".join(dependencies[1]))
    if(getVar):            
        for n, dependency in enumerate(dependencies[1]):
            if not(dependency.strip() in axiomVarReport.keys()):
                axiomVarReport[dependency.strip()] = {"models" : [], "dependencies" : [], "parent" : []}
                if(aggregationName == "CR_SA_Capital_Requirements_Pre"):
                    if(dependencies[0][n].strip() in modelPreAggParams.keys()):
                        axiomVarReport[dependency.strip()]["models"].append(modelPreAggParams[dependencies[0][n].strip()])
                        if(dependencies[0][n].strip() == "Aggregation") or (dependencies[0][n].strip() == "eu_cr_exposure"):
                            axiomVarReport[dependency.strip()]["dependencies"].extend(getDependenciesOfCalc(dependency.strip()))
                    else:
                        axiomVarReport[dependency.strip()]["models"].append(dependencies[0][n].strip())
                    axiomVarReport[dependency.strip()]["parent"].append("Pre")
                else:
                    if(dependencies[0][n].strip() in modelAggParams.keys()):
                        axiomVarReport[dependency.strip()]["models"].append(modelAggParams[dependencies[0][n].strip()])
                    if(dependencies[0][n].strip() == "Aggregation") or (dependencies[0][n].strip() == "eu_cr_exposure"):
                        axiomVarReport[dependency.strip()]["dependencies"].extend(getDependenciesOfCalc(dependency.strip()))
    else:
        if(len(dependencies[1]) >= 1):
            getValuesOfVariables(nodesName.strip(), aggregationName, dependencies[1], dependencies[0])
        else:
            getValuesOfVariables(nodesName.strip(), aggregationName, [nodes["param"][1]["string"]], ["HardCodeado"])
    return index + 1
    

#Enter all the Origin and Expressions for the differents attributes in an Aggregation
def enterAggregation(jsonArchive, workSheetParam, aggregationName, getVar):
    global axiomVarReport
    varExpression = ""
    varName = ""
    index = 1
    listOfModels = {}
    print(aggregationName)
    for parameterNode in jsonArchive["nodes"]["parameterNode"]["parameterNode"]:
        if(isinstance(parameterNode["parameterNode"], dict)):
            index = analyzeParameterNode(workSheetParam, parameterNode["parameterNode"]["parameters"]["param"]["paramLine"], parameterNode["parameterNode"]["_name"], index, aggregationName, getVar)
        else:
            for nodes in parameterNode["parameterNode"]:
                if (isinstance(nodes["parameters"]["param"]["paramLine"], list)):
                    for paramLine in nodes["parameters"]["param"]["paramLine"]:
                        index = analyzeParameterNode(workSheetParam, paramLine, nodes["_name"], index, aggregationName, getVar)
                else:
                    index = analyzeParameterNode(workSheetParam, nodes["parameters"]["param"]["paramLine"], nodes["_name"], index, aggregationName, getVar)
                indexSheet = 9
    workSheetParam.autofilter(0, 0, index, 8)
    setColumnsWidth(workSheetParam)
    return varExpression        


def getModelFromAgg(model):
    switcher = {"position": "PositionCalc_Input", "position_ref_position": "PositionCalc_Input", "cashflow": "CashflowCalc_Input", "cashflow_ref_position": "CashflowCalc_Input", "counterparty": "CounterpartyCalc_Input", }
    modelResult = switcher.get(model, model)
    return modelResult

#Get all the condition for each Register
index = 1
for aggregationName in aggregationNames:
    print(aggregationName)
    workSheetAggregation = newAggregationSheet(aggregationName)
    with open("CapitalAggregations/Aggregation" + aggregationName + ".json") as jsonAggregation:
        jsonAggregationpy = json.load(jsonAggregation)
        enterAggregation(jsonAggregationpy, workSheetAggregation, aggregationName, True)

jsonArchives = getJSON("/home/cano057/VisualStudio/Axiom/Capital/mapping")
for jsonArchive in jsonArchives:
    informPath = "mapping/" + jsonArchive
    informName = jsonArchive.split(".")[0]
    #Get Registers from Nodes
    with open(informPath) as jsonRegistersNodes:
        jsonRegisterNodespy = json.load(jsonRegistersNodes)
        enterAggregation(jsonRegisterNodespy, workSheetAggregation, informName, False)




def createSheetWithVars():
    worksheetVar = workbook.add_worksheet("Relación reporte variables")
    worksheetVar.write(0, 0, "Reporte", header_format)
    worksheetVar.write(0, 1, "Variable Axiom", header_format)
    worksheetVar.write(0, 2, "Dependencia", header_format)
    worksheetVar.write(0, 3, "Alias", header_format)
    worksheetVar.write(0, 4, "Comentarios", header_format)
    worksheetVar.freeze_panes(1, 1)
    return worksheetVar

def fillSheetVar(worksheetVar):
    index = 1
    print(axiomVarReport)
    for var in axiomVarReport.keys():
        worksheetVar.write(index, 0, " ".join(axiomVarReport[var]["models"]))
        worksheetVar.write(index, 1, var)
        worksheetVar.write(index, 2, " ".join(axiomVarReport[var]["dependencies"]))
        worksheetVar.write(index, 3, " ".join(axiomVarReport[var]["parent"]))
        index = index + 1

fillSheetVar(createSheetWithVars())
workbook.close()