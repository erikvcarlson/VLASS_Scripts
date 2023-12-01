#Author: Erik Carlson 
#Description: This Script takes a user provided Right Ascention and Declination in Decimal Format and provides the user with the required measurement sets
#This script requires the use of Python 3 to run properly 
#Note This Script Fails if the Archive is Down
import urllib
import urllib.request
import re
import csv
import requests
import pandas as pd
from scipy.optimize import fsolve
import numpy as np 

def unique(list1):
 
    # intilize a null list
    unique_list = []
     
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    return(unique_list)


#intake and validate values from the user
a = 0

while a ==0: 
    try: 
        RA = input("Please Enter your Right Ascension in Decimal Format: ") #121.98974
        DEC = input("Please Enter your Declination in Decimal Format: ") #4.54293
        Im_Size = input("Please Enter the Proposed Image Size to the nearest Arcsecond: ")
        percent_of_primary_beam = 0.17
        advanced_options = input("Advanced Options (Y/n): ")
        if advanced_options == 'Y': 
            percent_of_primary_beam = input("What fraction of the full sensitivity of the primary beam would you like to sample: (i.e 0.17 is the standard 1000 arcseconds): ")
        RA = float(RA)
        DEC = float(DEC)
        if Im_Size == '':
            Im_Size = '250'
        Im_Size = int(Im_Size)
        break
    except: 
        print("Incorrect Values Entered")

data = pd.read_fwf('https://archive-new.nrao.edu/vlass/VLASS_dyn_summary.php', sep = ' ',skiprows=[1,2], header = 0)

def primary_beam(x, y):
    return (1.0/315.0) * 2**(-1 - (x**2)/396900.0) * np.sqrt(np.log(2)/np.pi) / (1.0/630.0 * np.sqrt(np.log(2)/np.pi)) - y


# Initial guess for the root
initial_guess = 0.0

# Solve the equation numerically for x
buffer = fsolve(primary_beam, initial_guess, args=(float(percent_of_primary_beam)))

Im_Size_Degrees = Im_Size/3600 + 2 * buffer/3600

        
RA_Right = RA + Im_Size_Degrees/2
RA_Left = RA - Im_Size_Degrees/2
if RA_Left < 0: 
    RA_Left = RA_Left + 360
if RA_Right >= 360: 
    RA_Right = RA_Right - 360

Dec_Up = DEC + Im_Size_Degrees/2
Dec_Down = DEC - Im_Size_Degrees/2

measurement_set_list = []
stated_tile = False
other_tiles = []
VLASS_id_list = []
warning = False
qa_rejected_list = []
for index, tile in data.iterrows():
    Dec_Tile_Start = tile['Dec min']
    Dec_Tile_End = tile['Dec max']
    Dec_Tile_Center = (Dec_Tile_End - Dec_Tile_Start)/2 + Dec_Tile_Start
    RA_Tile_Start = tile['RA min']*15
    RA_Tile_End = tile['RA max']*15
    RA_Tile_Center = (RA_Tile_End - RA_Tile_End)/2 + RA_Tile_Start
        
    RA_L = [RA, RA_Left, RA_Right,RA_Left,RA_Right,  RA, RA, RA_Left, RA_Right]
    DEC_L = [DEC, Dec_Up, Dec_Down, Dec_Down, Dec_Up,  Dec_Up, Dec_Down, DEC, DEC]

    for i in range(0,len(RA_L)):
        if RA_L[i] > RA_Tile_Start and RA_L[i] < RA_Tile_End and DEC_L[i] > Dec_Tile_Start and DEC_L[i] < Dec_Tile_End:
            tile_id = tile[0]
            VLASS_id = tile[5]
            VLASS_id_list.append(VLASS_id)
            if i == 0 and stated_tile == False:
                stated_tile = True
                primary_tile = tile_id
                print('Your image phasecenter resides in tile: ' + tile_id)
            if tile_id != primary_tile:
                other_tiles.append(tile_id)

            if VLASS_id == 'VLASS1.1' or VLASS_id == 'VLASS1.2':
                VLASS_id_url = VLASS_id + 'v2'
            else: 
                 VLASS_id_url = VLASS_id

            URL = "https://archive-new.nrao.edu/vlass/quicklook/" + VLASS_id_url + '/' + tile_id + '/'
            page = requests.get(URL).text

            JName_regex = 'J\d{6}[+|-]\d{6}[.]\d\d[.]\d{4}\S{3}'
            m = re.search(JName_regex, page)

            if m:
                found_JName = m.group(0)
                full_directory_name = VLASS_id + '.ql.' + tile_id + '.' + found_JName
                URL_New = "https://archive-new.nrao.edu/vlass/quicklook/" + VLASS_id_url + '/' + tile_id + '/' + full_directory_name + '/casa_pipescript.py'
                try:
                    url = URL_New
                    search_file_for_ms =  urllib.request.urlopen(url)
                    for line in search_file_for_ms:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.find(str(VLASS_id)) != -1:
                            start_value = int(decoded_line.find(str(VLASS_id)))
                            end_value = int(decoded_line.find('.ms'))
                            measurement_set_name = decoded_line[start_value:end_value]
                            measurement_set_list.append([measurement_set_name.strip('_split'),tile_id])
                except:
                    pass
            if not m:
                JName_regex = str(tile_id) + '[.]J\d{6}[+|-]\d{6}[.]\d\d[.]\d{4}\S{3}'
                URL = "https://archive-new.nrao.edu/vlass/quicklook/" + VLASS_id_url + '/QA_REJECTED/' 
                page = requests.get(URL).text
                m1 = re.search(JName_regex, page)
                if m1: 
                    found_JName = m1.group(0)
                    full_directory_name = VLASS_id + '.ql.' + found_JName
                    URL_New = "https://archive-new.nrao.edu/vlass/quicklook/" + VLASS_id_url + '/QA_REJECTED/' + full_directory_name + '/casa_pipescript.py'                
                    print('WARNING - ALL OF THE IMAGES FROM ' + VLASS_id + '/' + tile_id + ' are QA Rejected')
                try:
                    url = URL_New
                    search_file_for_ms =  urllib.request.urlopen(url)
                    for line in search_file_for_ms:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.find(str(VLASS_id)) != -1:
                            start_value = int(decoded_line.find(str(VLASS_id)))
                            end_value = int(decoded_line.find('.ms'))
                            measurement_set_name = decoded_line[start_value:end_value]
                            measurement_set_list.append([measurement_set_name.strip('_split'),tile_id])
                except:
                    pass

print('Your image also draws data from tile(s): ' + ' '.join(list(set(other_tiles))))
                    
for i in range(len(unique(measurement_set_list))):
    print(unique(measurement_set_list)[i][0] + ' - MS contains data or tile: ' + unique(measurement_set_list)[i][1] )