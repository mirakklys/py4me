### imports

import os
import json

### directory to process csv

workingDir = os.getcwd() + '\\toProcess'
# print(workingDir)
# print(os.listdir(workingDir))

### processing csv

# function to handle complex csv format
def cleanSubstrings(astr, divider = '"', charToSave = ',', changeWith = ':'):

    # define " positions
    alist = []
    count = 0
    
    for each in astr:
        if each == divider:
            alist.append(count)
        count += 1

    anotherList = []
    
    # creating list of each line in the file
    for each in range(len(alist)):
        if each == 0:
            anotherList.append(astr[:alist[0]])
            anotherList.append(astr[alist[0]:(alist[1] + 1)])
        elif each == len(alist) - 1:
            anotherList.append(astr[(alist[-1] + 1):])
        else:
            anotherList.append(astr[(alist[each] + 1):(alist[each + 1] + 1)])
    
    difList = []
    
    # changing csv divider from , to : leaving the commas from ""
    for each in anotherList:
        dif = None
        if divider in each:
            dif = each.replace(divider, '')
        else:
            dif = each.replace(charToSave, changeWith)
        difList.append(dif)
    
    return ''.join(difList)

    ### processing csv files 
filesToOpen = []

# the csv files should be placed in toProcess subfolder
for each in os.listdir(workingDir):
    if '.csv' in each:
        filesToOpen.append(workingDir + '\\' + each)

# creating final dictionary
countryDict = {}

for fileToOpen in filesToOpen:
    with open(fileToOpen) as inp:
        swissKnife = [each.strip() for each in inp][2:]

    tempFilesToOpen = []

    for each in swissKnife:
        if '"' not in each:
            tempFilesToOpen.append(each.replace(',',':'))
        else:
            tempFilesToOpen.append(cleanSubstrings(each))

    for each in tempFilesToOpen:
        tempList = each.split(':')
        countryDict[tempList[3]] = countryDict.get(tempList[3], {}) 
        countryDict[tempList[3]][tempList[2]] = countryDict[tempList[3]].get(tempList[2], {})
        countryDict[tempList[3]][tempList[2]][tempList[0]] = countryDict[tempList[3]][tempList[2]].get(tempList[0], tempList[-1].strip())

### optional creation of JSON file, if anybody needs to use it in other coding languages
countryJson = json.dumps(countryDict, indent = 2)
with open('countries.json', 'w') as f:
    f.write(countryJson)

### creating gline.js files for each variant in separate folders
with open('countries.json') as f:
    temp = json.load(f)

tempNames = [each for each in temp]

tempDir = [each.replace('$','_').replace(' ', '_').replace('%','_percent_').replace('(', '-').replace(')', '-').replace('/','-').replace(':', '-') for each in tempNames]
for each in tempDir:
    os.mkdir(each)

### both gline.js and gline.htm files are created 
for i in range(len(tempNames)):
    gline = [['Year', ]]
    filename = tempNames[i]

    tempCountry = []
    tempYears = sorted([each.strip() for each in temp[filename]])

    for every in tempYears:
        for each in temp[filename][every]:
            if each not in tempCountry:
                tempCountry.append(each.strip())
    tempCountry = sorted(tempCountry)    
    for each in range(len(tempYears)):
        gline.append([tempYears[each]])

    for each in tempCountry:
        gline[0].append(each.strip())

    for each in range(1, len(tempYears) + 1):
        for every in range(1, len(tempCountry) + 1):
            if tempCountry[every - 1] in temp[filename][tempYears[each - 1]]:
                gline[each].append(round(float(temp[filename][tempYears[each - 1]][tempCountry[every - 1]]), 2))
            else:
                gline[each].append(None)
                
    with open(tempDir[i] + '\\gline.js', 'a') as f:
        f.write('gline = ')
        f.write(json.dumps(gline))
        
    with open(tempDir[i] + '\\gline.htm', 'a') as htm:
        htm.write('''<html>
  <head>
    <script type="text/javascript" src="gline.js"></script>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable( gline );

        var options = {
          title: \'''' + filename + '''\',
          chartArea: {left:'10%',top:'10%', width: '65%', height: '65%'}
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>
  </head>
  <body>
    <div id="chart_div" style="width: 1300px; height: 600px;"></div>
    <a href="..\index.htm">Go Back</a>
  </body>
</html>
''')
        
### index.htm file with all hyperlinks to the graphs
indexHtm = open('index.htm', 'a')
indexHtm.write('''<html>
  <head>
   <title>Index page</title>
  </head>
  <body>''')
for each in tempDir:
    indexHtm.write('<p><a href="' + each + '\\gline.htm">' + each + '</a></p>')
    
indexHtm.write('''  </body>
</html>''')
indexHtm.close()