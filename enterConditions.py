import json

print "Leyendo archivos"
#f = open('xml.json')
#g = open('jsoncolumns.json')
#xmlGeneral = json.load(f)
#conditions = json.load(g)
with open('data.json') as xml:
    xmlpy = json.load(xml)
    with open('data (1).json') as jsoncolumns:
        jsoncolumnspy = json.load(jsoncolumns)

        def changeCondition(name, i, array):
            print name
            if len(array["CONDITION"]["CONDITION"]) > 0:
                print "hecho"
                jsoncolumnspy["JSONCOLUMNS"]["CONDITION"][i]["name"] = name
                i = i+1
            if len(array["portfolio-node"]) > 0:
                for portf in array["portfolio-node"]:
                    name = array["_name"]
                    if (isinstance(portf, dict) == False):
                        changeCondition(name, i, portf)
                    elif((len(v) for v in portf.values()) > 2 ):
                        print portf.keys()
                        changeCondition(name, i, portf)

        changeCondition( xmlpy["nodes"]["portfolio-node"]["_name"], 0, xmlpy["nodes"]["portfolio-node"])

#f.close()
#g.close()