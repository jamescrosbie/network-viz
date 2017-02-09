from flask import Flask, render_template, request, jsonify
import json
import pandas as pd


app = Flask(__name__)


global path , data
path = '~/Desktop/James/Workings/FlaskApp/Data/'
data = pd.read_csv(path +'patientpathway.csv',#nrows=5000,
                    dtype = {'Sex':str,'nodeIn':str,'nodeOut':str,
                                'year':str,'month':str,'activityType':str,
                                'ageBand':str,'Provider':str,'CCG':str}) 


def listFun(df,columnNames):
    newlist =[]
    for i in df[list(columnNames)]:
        a = list(set(df[i].tolist()))
        a.sort()
        a = ["All"] + a
        newlist.append(a)
    return newlist


def removeAll(val1,val2):
    if val1 == ["All"] :
        return listFun(data,[val2])[0][1:]  
    else :
        return val1


def makeConnections(df):   
    connections = []
    for i in range(len(df)):
        dic = {}
        dic['source'] = df['textIn'].iloc[i]
        dic['target'] = df['textOut'].iloc[i]
        connections.append(dic)

    seen = set()
    new_l = []
    for d in connections:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    
    connections = []
    for i in new_l:
        i['flow'] = len( df[ ( df['textIn'] == i['source'] ) & ( df['textOut'] == i['target'] ) ] )
        connections.append(i)
    
    return connections
 

def makeNodes(df):
    fulllist = df['textIn'].append(df['textOut'])
    fl2 = list(set(fulllist.drop_duplicates().tolist()))

    nodes = []
    for i in fl2:
        dic = {}
        dic['name'] = i

        b = df[ df['textIn'] == i ]
        if len(b) == 0:
            b = df[ df['textOut'] == i ]
        dic['size']  = len(b)
        nodes.append(dic) 
    return nodes


def stringConvert(myList):
    if myList == [] :
        myList = ['All']
    else:
        myList = list(set(myList))
        myList = [str(x) for x in myList ]    
    return myList


def getMonthNames(val):
    if val == '1' :
        monthName = 'Jan'
    if val == '2' :
        monthName = 'Feb'
    if val == '3' :
        monthName = 'Mar'       
    if val == '4' :
        monthName = 'Apr'
    if val == '5' :
        monthName = 'May'
    if val == '6' :
        monthName = 'Jun'  
    if val == '7' :
        monthName = 'Jul'
    if val == '8' :
        monthName = 'Aug'
    if val == '9' :
        monthName = 'Sep'
    if val == '10':
        monthName = 'Oct'
    if val == '11' :
        monthName = 'Nov'
    if val == '12' :
        monthName = 'Dec'  
    return monthName


def sortMonths(mynames):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul','Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    order = {v: i for i,v in enumerate(months)}
    return mynames.sort(key=lambda x: order[x])


def getMonthNumber(mynames):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul','Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    order = {v: i for i,v in enumerate(months)}
    
    if 'All' in mynames :
        return  [ str(i) for i in range(1,13) ]
    else :
        return  [ str(order[j] + 1)  for j in mynames ]     


def makeData(myYear,myMonth,myAge,mySex,myProv,myComm,myCond,myMin,myMax):
    myYear = stringConvert(myYear)
    myYear  = removeAll(myYear,'year')
    myMonth = removeAll(myMonth,'month')
    myAge   = removeAll(myAge,'ageBand') 
    myProv  = removeAll(myProv,'Provider') 
    myComm  = removeAll(myComm,'CCG')
    myCond  = removeAll(myCond,'activityType')

    tempS = []
    for s in mySex:
        if s =='Male':
            tempS.append('1')
        if s == 'Female':
            tempS.append('2')
        if s == 'All':
            tempS.append('1')
            tempS.append('2')

    print myYear, myMonth, myAge, tempS, myProv, myComm, myCond, myMin, myMax

    df = data [ data['year'].isin(myYear) &
                data['month'].isin(myMonth) & 
                data['ageBand'].isin(myAge) &
                data['Sex'].isin(tempS) &
                data['Provider'].isin(myProv) & 
                data['CCG'].isin(myComm) &
                data['activityType'].isin(myCond) &
                ( data['Cost'] >=  float(myMin) ) & 
                ( data['Cost'] <= float(myMax) )
            ]

    nodes = makeNodes(df)    
    links = makeConnections(df)

    myFile = {}
    myFile['links'] = links
    myFile['nodes'] = nodes

    with open('myJSONfile.json', 'w') as outfile:  
        json.dump(myFile, outfile,indent = 4)

    return json.dumps(myFile)


@app.route('/')
@app.route('/index',methods=['POST','GET'])
def index():    

    years, months = listFun(data,['year','month'])
    years2 = years[1:]
    years2.sort(reverse=True)
    years = ['All'] + years2

    ages, conditions  = listFun(data,['ageBand','activityType'])
    conditions = [x for x in conditions if str(x) not in ['nan','&','0'] ]
    sexs = ['Male','Female']
    providers, commissioners = listFun(data,['Provider','CCG'])

    monthNames = [getMonthNames(x) for x in months if x != 'All']
    sortMonths(monthNames)
    monthNames = ['All'] + monthNames

    formMin = data['Cost'].min()
    formMax = data['Cost'].max()

    if request.method == 'POST':
        
        myYear = request.form.getlist('yearSelected')  
        myMonth = request.form.getlist('monthSelected')
        myAge = request.form.getlist('ageSelected')
        mySex = request.form.getlist('sexSelected')
        myProv = request.form.getlist('providerSelected')
        myComm = request.form.getlist('ccgSelected')
        myCond = request.form.getlist('conditionSelected')
        myMin = request.form.get('myMin')
        myMax = request.form.get('myMax')   
        
        
        #Test Values
        '''
        myYear = ['2016']
        myMonth = ['Mar']
        myAge  = ['11-20']
        mySex  = ['Female']
        myProv = ['All']
        myComm = ['All']
        myCond = ['100']
        myMin = float(120)
        myMax = float(900)
        '''
       
        myYear = ['All'] if not myYear else myYear
        myMonth = ['All'] if not myMonth else myMonth
        myMonth = getMonthNumber(myMonth)
        myAge = ['All'] if not myAge else myAge
        mySex = ['All'] if not mySex else mySex
        myProv   = ['All'] if not myProv else myProv  
        myComm  = ['All'] if not myComm else myComm 
        myCond  = ['All'] if not myCond else myCond

        if myMax < myMin :
            myMin, myMax = myMax, myMin

        jsonFile = makeData(myYear,myMonth,myAge,mySex,myProv,myComm,myCond,myMin,myMax)
        results = jsonFile
    else:    
        results = []
                            
    return render_template("systemPatientFlows v6.html",
                                years = years,
                                months = monthNames,
                                sexs = sexs,
                                ages = ages,
                                conditions = conditions,
                                providers = providers,    
                                commissioners = commissioners,
                                formMin = formMin, formMax = formMax,
                                results = results)

if __name__ == '__main__':
   app.run(debug=True)  
