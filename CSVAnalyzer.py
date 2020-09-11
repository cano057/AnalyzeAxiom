import pandas as pd

def getDataFrame(csvfile):
    dataframeVar = pd.read_csv(csvfile, index_col = 0, dtype = "str")
    print("DataFrame created")
    return dataframeVar

def deleteRepeteadData(dataframeVar):
    resultVar = {}
    for column in dataframeVar.columns:
        lista = list(set(dataframeVar[column]))
        resultVar[column] = lista
    return resultVar

def modifyFormat(stringValue, formatValue):
    if(((stringValue[(len(stringValue)- len(formatValue)) :]) != formatValue) or ((len(stringValue)- len(formatValue)) <= 0)):
        print (stringValue + formatValue)
        return (stringValue + formatValue)
    else:
        print ("correct format")
        return stringValue

def getName():
    option = ""
    name = ""
    name = input("Teclee el nombre del archivo csv con los datos a analizar o end para terminar\n")
    return name

def getNamesForConsole():
    names = []
    valor = ""
    while (valor != "end"):
        valor = getName()
        if valor != "end":
            valor = modifyFormat(valor, '.csv')
            names.append(valor)
    return names

csvNamesFile = getNamesForConsole()
dfFiles = []
for csvName in csvNamesFile:
    dataframeCsv = getDataFrame(csvName)
    dictdataframe = deleteRepeteadData(dataframeCsv)
    #removes the null values
    for key in dictdataframe.keys():
        dictdataframe[key] = [x for x in dictdataframe[key] if x == x]
    maxLenght = 0
    #gets the max length
    print("end1")
    for key in dictdataframe.keys():
        if (len(dictdataframe[key]) > maxLenght):
            maxLenght = len(dictdataframe[key])
    print("end2")
    #insert empty items to reach the correspondant length
    for key in dictdataframe.keys():
        if(len(dictdataframe[key]) < maxLenght):
            if not(isinstance(dictdataframe[key], list)):
                dictdataframe[key] = []
                print("no es una lista")
            for i in range(maxLenght - len(dictdataframe[key])):
                dictdataframe[key].append("")
    
            
    df = pd.DataFrame.from_dict(dictdataframe)
    df.to_csv(csvName.split(".")[0] + "_result" + ".csv", index = False, header=True)




    
