## User-Defined Imaging of the Very Large Array Sky Survey

The following github repository can be use to generate custom VLASS images of a target source. This "Read Me" will serve as a supplement to the VLASS Memo 20: Utilzing a Customized VLASS Single Epoch Continuum Pipeline for End-User Science. 

If a bug is encountered, please email akimball@nrao.edu or erikvcarlson@uri.edu with the RA, DEC, desired science image size and any error messages that you received.  


#### Identifying the Requisite Measurement Set

The first step in generating an image is to identify which measurement set (MS) your data resides. While you may already have previous knowledge where your data resides, it is still beneficial to utilize this tool to ensure your source does not reside on the border of two or more observations. 

To identify where your data resides, we will use the VLASS_Tile_Puller.py script located in the Measurement_Set_Identification folder of this repository. This code can be run inside of CASA or inside of an iPython environment like Jupyter Notebook or Google Colab.

For this tutorial, we will use the same radio-loud quasar, J0807+0432, as the Appendix in VLASS Memo 20 and will generate a science image of 500"x500". 


```python
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
```

    Please Enter your Right Ascension in Decimal Format: 121.98974
    Please Enter your Declination in Decimal Format: 4.54293
    Please Enter the Proposed Image Size to the nearest Arcsecond: 250
    Advanced Options (Y/n): Y
    What fraction of the full sensitivity of the primary beam would you like to sample: (i.e 0.17 is the standard 1000 arcseconds): 0.17

    Your image phasecenter resides in tile: T12t13
    Your image also draws data from tile(s): 
    VLASS2.1.sb38561374.eb38565040.59070.62333981482 - MS contains data or tile: T12t13
    VLASS1.1.sb34647560.eb34700758.58075.26425702547 - MS contains data or tile: T12t13
    VLASS3.1.sb43247986.eb43449519.59968.0862703125 - MS contains data or tile: T12t13


For the purposes of this guide, we will use the VLASS2.1.sb38561374.eb38565040.59070.62333981482 measurement set. To obtain our calibration products, we will go to data.nrao.edu. We will simply copy the string: VLASS2.1.sb38561374.eb38565040.59070.62333981482 into the search box. 

After selecting the "cross button" just before the project name, we can click the clipboard and then the "Download" button. 

When presented with the "Launch Workflow Task on: VLASS2.1" pop-up, if you are signed into your NRAO account, you edit the Destination Directory to put the data directly into your lustre account. It is not recommended that you request the products to be returned as a tarball as this can increase the turnaround time to several days. 

#### Preparing a Working Directory 
While we are waiting for the data to be transfered, we need to prepare a working directory. The working directory must have the following scripts: 

1) SEIP_parameter.list
2) command_script.py
3) run_SE.sh

##### SEIP_parameter.list

The SEIP_parameter.list is a simple text file with the several keyword arguements used by the VLASS imaging pipeline. A sample file is located in the Run_Files directory of this repository. For this example, we will use the following lines in our SEIP_parameter.list file:


```python
imagename='VLASS_Tutorial' #image name - can not contain spaces
phasecenter='J2000 08:07:57.68 +04.32.34.55' #phasecenter of the image the user wants to image. Typically centered on the source
imaging_mode='VLASS-SE-CONT-MOSAIC' #Leave unchanged 
imsize=[3125,3125] #image size in pixels to include the buffer 
cell='0.6arcsec' #cell size as defined by the user
```

Note, the `imsize` argument is the image size in pixels including the buffer. To calculate the image size, take the desired cell size (0.6" in this case), and divide it by your image size plus the buffer, which is typically 1380 arcseconds. For example, for a 500" science image:

(500+1380)/0.6 = 3133 pixels

For CASA's `tclean` parameter to run efficiently, the image size should be a power of 2, 3, 5, or 7. You can use the following code to identify the closest pixel size which is equal to one



```python
factor_2 = []
factor_3 = []
factor_5 = []
factor_7 = []
for i in range(1,25):
    factor_2.append(2**i)
    factor_3.append(3**i)
    factor_5.append(5**i)
    factor_7.append(7**i)
    
factor_list = factor_2 + factor_3 + factor_5 + factor_7
factor_list.sort()
#this cannot be odd 

def closest(lst, K):
      
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
      
# To calculate the value K, take the desire cell size (default 0.6 arcseconds) and divide it by your imagesize plus the buffer (1380 arcseconds)
# For example (500+1380)/0.6 = 3133 which should be your value of K. This image size should then be appended to your image parameter list as 
# imsize = [K,K]
# if other than the default cell size is to be used then the user should also append the cell size to the image parameter list for 
# example cell = ['0.4arcsec','0.4arcsec']

K = 3133
print(closest(factor_list, K))
```

    3125


##### run_SE.sh

The next file that needs to be located in our working directory is our SLURM script. This can be replaced with a similar script for Torque schedulers or can be removed altogether if reducing the data on your local machine. For this tutorial, we will assume we are reducing the data on the NRAO compute cluster and will use the following script:



```shell
#!/bin/bash

#SBATCH --cpus-per-task=1   # Amount of memory needed by each process (ppn) in the job.
#SBATCH --mem=64GB
#SBATCH --export=ALL


# casa's python requires a DISPLAY for matplot, so create a virtual X server
xvfb-run -d /home/casa/packages/pipeline/casa-6.4.1-12-pipeline-2022.1.1.5/bin/casa --pipeline --nogui --nologger -c  command_script.py
```

##### command_script.py

The final file that needs to be in our working directory to run our data is the `command_script.py`. This file contains the primary instructions for CASA to successfully image our data. Again, a sample of this script is located in the `Run_Files` directory in this repository.



```python
__rethrow_casa_exceptions = True #standard
context = h_init() #standard
context.set_state('ProjectSummary', 'proposal_code', 'VLASS') #standard
context.set_state('ProjectSummary', 'proposal_title', 'unknown') #standard
context.set_state('ProjectSummary', 'piname', 'unknown') #standard
context.set_state('ProjectSummary', 'observatory', 'Karl G. Jansky Very Large Array') #standard
context.set_state('ProjectSummary', 'telescope', 'EVLA') #standard
context.set_state('ProjectStructure', 'ppr_file', 'PPR.xml') #standard
context.set_state('ProjectStructure', 'recipe_name', 'hifv_vlassSEIP') #standard
try:
    hifv_importdata(nocopy=True, vis=['JXXXX+XXXX_VLASS_split.ms'], session=['session_1'])
    #change the vis variable to the location of your measurement set
    hif_editimlist(parameter_file='SEIP_parameter.list')
    #change the parameter_file to your image parameter file
    hif_transformimagedata(datacolumn='data', clear_pointing=False, modify_weights=True, wtmode='nyq')
    hifv_vlassmasking(maskingmode='vlass-se-tier-1', vlass_ql_database='/home/vlass/packages/VLASS1Q.fits')
    hif_makeimages(hm_masking='manual')
    hifv_checkflag(checkflagmode='vlass-imaging')
    hifv_statwt(statwtmode='VLASS-SE', datacolumn='residual_data')
    hifv_selfcal(selfcalmode='VLASS-SE')
    hif_editimlist(parameter_file='SEIP_parameter.list')
    #change the parameter_file to your image parameter file
    hif_makeimages(hm_masking='manual')
    hif_editimlist(parameter_file='SEIP_parameter.list')
    #change the parameter_file to your image parameter file
    hifv_vlassmasking(maskingmode='vlass-se-tier-2')
    hif_makeimages(hm_masking='manual')
    hifv_pbcor(pipelinemode="automatic")
    hif_makermsimages(pipelinemode="automatic")
    hif_makecutoutimages(pipelinemode="automatic")
    hif_analyzealpha(pipelinemode="automatic")
    # hifv_exportvlassdata(pipelinemode="automatic") 
    # uncomment above if the user wants the data to be exported to the products directory 
finally:
    h_save()

```

Do note that before we run this script, we need to change the text "JXXXX+XXXX_VLASS_split.ms" to whatever we have named our split-off measurement set.

#### Splitting Off our Desired Data

By now, our measurement set should either be directly written to our Lustre account or we have used wget to transfer the data to its destination. Once our data is now in our working directory, we can split off the required fields for imaging to save both disk space and time. First, we will open an instance of CASA inside of our working directory. We will then need to copy the `carlson_editimlist_prep` function located in the `carlson_editimlist_prep.py` file from the `Field_Selector` directory of this repository into CASA.



```python
def carlson_editimlist_prep(msfile, imagesize, phase_center, matchregex=['^0', '^1', '^2']):
#must be run with VLASS version of CASA to allow for casa_tools to work properly
#carlson_editimlist_prep('VLASS2.1.sb38561374.eb38565040.59070.62333981482.ms/',500,'J2000 08:07:57.5 +04.32.34.6', matchregex=['^0', '^1', '^2'])       
    from pipeline.infrastructure import casa_tools
    import numpy
    
    buffer_arcsec = 1000 #Primary beam in arcseconds at 17%
    dist_arcsec = imagesize/2 + buffer_arcsec
    dist_arcsec = str(dist_arcsec) + 'arcsec'
    distance = dist_arcsec
    
    # Created STM 2016-May-16 use center direction measure
    # Returns list of fields from msfile within a rectangular box of size 2 * distance

    qa = casa_tools.quanta
    me = casa_tools.measures
    tb = casa_tools.table

    #msfile = self.vislist[0]

    fieldlist = []

    phase_center = phase_center.split()
    print(phase_center)
    center_dir = me.direction(phase_center[0], phase_center[1], phase_center[2])
    center_ra = center_dir['m0']['value']
    center_dec = center_dir['m1']['value']

    try:
        qdist = qa.toangle(distance)
        qrad = qa.convert(qdist, 'rad')
        maxrad = qrad['value']
    except:
        print('ERROR: cannot parse distance {}'.format(distance))
        return

    try:
        tb.open(msfile + '/FIELD')
    except:
        print('ERROR: could not open {}/FIELD'.format(msfile))
        return
    field_dirs = tb.getcol('PHASE_DIR')
    field_names = tb.getcol('NAME')
    tb.close()

    (nd, ni, nf) = field_dirs.shape
    print('Found {} fields'.format(nf))

    # compile field dictionaries
    ddirs = {}
    flookup = {}
    for i in range(nf):
        fra = field_dirs[0, 0, i]
        fdd = field_dirs[1, 0, i]
        rapos = qa.quantity(fra, 'rad')
        decpos = qa.quantity(fdd, 'rad')
        ral = qa.angle(rapos, form=["tim"], prec=9)
        decl = qa.angle(decpos, prec=10)
        fdir = me.direction('J2000', ral[0], decl[0])
        ddirs[i] = {}
        ddirs[i]['ra'] = fra
        ddirs[i]['dec'] = fdd
        ddirs[i]['dir'] = fdir
        fn = field_names[i]
        ddirs[i]['name'] = fn
        if fn in flookup:
            flookup[fn].append(i)
        else:
            flookup[fn] = [i]
    print('Cataloged {} fields'.format(nf))

    # Construct offset separations in ra,dec
    print('Looking for fields with maximum separation in RA or DEC, {}, from the phase center'.format(distance))
    nreject = 0
    skipmatch = matchregex == '' or matchregex == []
    for i in range(nf):
        dd = ddirs[i]['dir']
        dd_ra = dd['m0']['value']
        dd_dec = dd['m1']['value']
        sep_ra = abs(dd_ra - center_ra)
        if sep_ra > numpy.pi:
            sep_ra = 2.0 * numpy.pi - sep_ra
        # change the following to use dd_dec 2017-02-06
        sep_ra_sky = sep_ra * numpy.cos(dd_dec)

        sep_dec = abs(dd_dec - center_dec)

        ddirs[i]['offset_ra'] = sep_ra_sky
        ddirs[i]['offset_ra'] = sep_dec

        if sep_ra_sky <= maxrad and sep_dec <= maxrad:
            if skipmatch:
                fieldlist.append(i)
            else:
                # test regex against name
                foundmatch = False
                fn = ddirs[i]['name']
                for rx in matchregex:
                    mat = re.findall(rx, fn)
                    if len(mat) > 0:
                        foundmatch = True
                if foundmatch:
                    fieldlist.append(i)
                else:
                    nreject += 1

    print('Found {} fields within {} rectolinear distance'.format(len(fieldlist), distance))
    if not skipmatch:
        print('Rejected {} distance matches for regex'.format(nreject))

    fieldlist = [str(i) for i in fieldlist]
    str1 = ','.join(fieldlist)
    fieldlist = str1 

    return fieldlist
```

After pressing enter to initialize the function, we can run the following command:


```python
field_list = carlson_editimlist_prep('VLASS2.1.sb38561374.eb38565040.59070.62333981482.ms/',500,'J2000 08:07:57.5 +04.32.34.6', matchregex=['^0', '^1', '^2'])       
```

This function will return a string to the variable `field_list`, which can be used with the `split` command in CASA to split off our data. The `split` command in CASA is:



```python
split(vis='VLASS2.1.sb38561374.eb38565040.59070.62333981482.ms/',outputvis='J0807+0432_split.ms',field=field_list)
```

Once our new measurment set is located in our working directory, we can remove the orginal "VLASS2.1.sb38561374.eb38565040.59070.62333981482.ms" measurement set. 

After changing the name of the measurment set in our command_script.py file, we can submit our run_SE.sh script to the slurm scheduler for the data to be imaged.  

If you use this script to generate your own user-defined images, please use the citation located in this Github Repository. 
```
