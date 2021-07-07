#Author: Erik Carlson 
#Description: This Script takes a user provided Right Ascention and Declination in Decimal Format and provides the user with the required measurement sets
#This script requires the use of Python 3 to run properly 
#Note This Script Fails if the Archive is Down
import urllib
import urllib.request
import re
import csv
import requests


#intake and validate values from the user
a = 0
while a ==0: 
    try: 
        RA = input("Please Enter your Right Ascention in Decimal Format: ") #121.98974
        DEC = input("Please Enter your Right Ascention in Decimal Format: ") #4.54293
        Epoch = input("Please Enter the Requested Epoch (1/2), leave blank if unknown: ")
        RA = float(RA)
        DEC = float(DEC)
        if Epoch == '':
            Epoch = '1'
        Epoch = int(Epoch)
        break
    except: 
        print("Incorrect Values Entered")

with open('Tile_Boundaries.csv', newline='') as csvfile:
    data = list(csv.reader(csvfile))

for tile in data:
        Dec_Tile_Start = float(tile[1])
        Dec_Tile_End = float(tile[2])
        Dec_Tile_Center = (Dec_Tile_End - Dec_Tile_Start)/2 + Dec_Tile_Start
        
        RA_Tile_Start = float(tile[3])*15
        RA_Tile_End = float(tile[4])*15
        RA_Tile_Center = (RA_Tile_End - RA_Tile_End)/2 + RA_Tile_Start
        
        if abs(RA_Tile_Center - RA) <= 3.75 and abs(Dec_Tile_Center - DEC) <= 2: 
            tile_id = tile[0]
            VLASS_id = tile[5]
            URL = "https://archive-new.nrao.edu/vlass/quicklook/" + VLASS_id + '/' + tile_id + '/'
            page = requests.get(URL).text
            JName_regex = 'J\d{6}[+]\d{6}[.]\d\d[.]\d{4}\S{3}'
            m = re.search(JName_regex, page)
            if m:
                found_JName = m.group(0)
                full_directory_name = VLASS_id + '.ql.' + tile_id + '.' + found_JName
                URL_New = "https://archive-new.nrao.edu/vlass/quicklook/" + VLASS_id + '/' + tile_id + '/' + full_directory_name + '/casa_pipescript.py'
                try:
                    url = URL_New
                    search_file_for_ms =  urllib.request.urlopen(url)
                    for line in search_file_for_ms:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.find(str(VLASS_id)) != -1:
                            start_value = int(decoded_line.find(str(VLASS_id)))
                            end_value = int(decoded_line.find('.ms'))
                            measurement_set_name = decoded_line[start_value:end_value]
                            print(measurement_set_name)
                except:
                    pass
            

