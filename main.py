import xlsxwriter

workbook = xlsxwriter.Workbook('dataF01.xlsx')
worksheet = workbook.add_worksheet()
f = open("demofile.txt", "r")
cadena = f.read()

pos = 0
pos2 = 0
posOp = 0
posOp2 = 0
posVal = 0
posVal2 = 0

#get the name
posNam = cadena.find('name="') + 8
posNam2 = cadena.find('"><CONDITION')
worksheet.write(0, 0, cadena[posNam:posNam2])

#put the name of the columns
worksheet.write(1, 0, "register name")
worksheet.write(1, 1, "var")
worksheet.write(1, 2, "operator")
worksheet.write(1, 3, "value")

#filter the text
posfilt = cadena.find("Current_assets") + 16
cadena = cadena[posfilt:]

#analyze the portfolio
i = 2
while ((cadena.find('name= "')) != -1):
    posReg = cadena.find('name= "') + 9
    posReg2 = cadena.find('"><CONDITION>')
    worksheet.write(i, 0, cadena[posReg:posReg2])
    i = i+1

    posTit = cadena.find('<CONDITION type="') + 17
    posTit2 = cadena.find('"><COLUMN')
    worksheet.write(i, 0, cadena[posTit:posTit2])

    while ((cadena.find("<COLNAME>")) != -1):
        pos = cadena.find("<COLNAME>") + 9
        pos2 = cadena.find("</COLNAME>")
        posOp = cadena.find("<OPERATION>") + 11
        posOp2 = cadena.find("</OPERATION>")
        posVal = cadena.find("<VALUE>") + 7
        posVal2 = cadena.find("</VALUE>")
        operator = cadena[posOp:posOp2].replace('=', "equal")
        worksheet.write(i, 0, cadena[pos:pos2])
        worksheet.write(i, 1, operator)
        worksheet.write(i, 2, cadena[posVal:posVal2])
        print(cadena[pos:pos2], operator, cadena[posVal:posVal2])
        i = i+1
        print('\n')
        cadena = cadena[(pos2+9):]
          
    cadena = cadena[(posReg2+9):]
  

workbook.close()