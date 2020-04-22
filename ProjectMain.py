### imports

from time import sleep 
import os
import json

### directory to process csv

workingDir = os.getcwd() + '\\toProcess'
# print(workingDir)
# print(os.listdir(workingDir))

### processing csv

## function to handle complex csv format
def cleanSubstrings(astr, divider = '"', toSave = ',', toChange = ':'):

    tempStr = astr
    tempList = []
    start = None
    end = None
    
    for each in range(tempStr.count(divider) + 1):
        if len(tempStr) > 1:
            for each in tempStr:
                if each == divider and tempStr.index(each) == 0:
                    start = 0
                    end = tempStr.replace(divider, '*', 1).find(divider) + 1
                    tempList.append(tempStr[start:end])
                    tempStr = tempStr[end:]
                    break
                elif each != divider and tempStr.index(each) == 0:
                    start = 0
                    end = tempStr.find(divider)
                    tempList.append(tempStr[start:end])
                    tempStr = tempStr[end:]
                    break
                elif divider not in each:
                    tempList.append(tempStr)
                    tempStr = ''
                    break
        else:
            break
    difList = []        
    for each in tempList:
        if divider not in each:
            difList.append(each.replace(toSave, toChange))
        else:
            difList.append(each.replace(divider, ''))
    
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
        if tempList[-1] == '':
            countryDict[tempList[3]][tempList[2]][tempList[0]] = countryDict[tempList[3]][tempList[2]].get(tempList[0], '0')
#             print('saved as 0', countryDict[tempList[3]][tempList[2]][tempList[0]])
        else:
            countryDict[tempList[3]][tempList[2]][tempList[0]] = countryDict[tempList[3]][tempList[2]].get(tempList[0], tempList[-1].strip())
#     print('{} is processed'.format(country))
#     sleep(0.1)

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
        
    with open(tempDir[i] + '\\gline.html', 'a') as htm:
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
          chartArea: {left:'10%',top:'10%', width: '75%', height: '75%'}
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>
  </head>
  <body>
    <p><a href="https://github.com/mirakklys/py4me">Git-Hub rep</a></p>
    <div id="chart_div" style="width: 1300px; height: 800px;"></div>
    <p><a href="..\\index.html">Go Back</a></p>
    <p><a href="data\\toProcess.zip">CSV files in archive</a>
  </body>
</html>
''')
        
### index.htm file with all hyperlinks to the graphs
indexHtm = open('index.html', 'a')
indexHtm.write('''<html>
  <head>
   <title>Index page</title>
  </head>
  <body>
    <p><a href="https://github.com/mirakklys/py4me">Git-Hub rep</a></p>
    <p><a href="data\\toProcess.zip">CSV files in archive</a></p>''')
for each in tempDir:
    indexHtm.write('<p><a href="' + each + '\\gline.html">' + each + '</a></p>')
    
indexHtm.write('''  </body>
</html>''')
indexHtm.close()
