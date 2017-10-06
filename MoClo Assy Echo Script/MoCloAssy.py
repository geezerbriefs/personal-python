"""
### MoClo Golden Gate Assembly Script ###

This script is designed to take in a .csv file containing the desired golden
gate parts mixtures for a DNA assembly, reference a list of DNA parts in a
library 384 well plate and perform the necessary calculations to create an
output .csv file that will be read by the Labcyte Echo "Plate Reformat"
software and direct the transfer of DNA from the library source plate to a
384 well Axygen PCR plate. The goal is an approximately equimolar mixture of
the requested parts in the assembly at ~4nM each in 4uL.

Created: 09/14/2017

Updated: 10/06/2017

Update Notes: It now handles the issue where a part's transfer volume is rounded
to zero due to really high concentration in the source plate. To address the issue
of unclear and ugly directory navigation for finding libraries and assembly files,
I just made it look directly in the current working directory for everything.
It is capable of finding each kind of file regardless of all the junk that may be
in the current directory. It works pretty great! Has been tested in powershell
and works from there.
"""
#Handles finding the files to be used in the script
import os

#Handles any operations we might do with lists and stuff
import numpy as np

#Handles our matrices and file i/o
import pandas as pd



"""Begin block of functions for getting the part library and assembly files"""

#gets a list of the parts libraries present in THE CURRENT PATH
def find_part_libraries_RM ():

    #Get name of directory where the current script, along with all other library and assembly files, lives
    currdir = os.getcwd()

    #go through all the items in this directory, files, folders, everything, then save only items that are files
    onlyfiles = [item for item in os.listdir(currdir) if os.path.isfile(currdir + '\\' + item)]

    #initialize list of possible library files
    libs = []

    for file in onlyfiles:
        #if file is an xlsx file (which library files should be)
        if(file[-4:]=='xlsx'):

            #read the excel file as a dictionary
            #with each sheetname generating a key for the dict to access each sheet individually
            xl_file = pd.read_excel(currdir + '\\' + file, sheetname=None)

            #check each sheet in that excel file
            for key in xl_file.keys():
                #check if the column labels 'part' and 'well' are in this sheet, if so, file is probably a library
                if ('part' in xl_file[key].columns and 'well' in xl_file[key].columns):
                    libs+=[('{}\\{}'.format(currdir, file), file[:-5])]

    return sorted(libs)[::-1]

#gets a list of the parts libraries present in a path
def find_part_libraries_ASS (path):

    #walkr holds generator object that has all the contents of the path directory and subdirectories
    walkr = os.walk(path)
    #convert to a list
    dirlist = list(walkr)

    #initialize list of possible library files
    libs = []

    #need dirlist[1][2] because os.walk gets a tuple (path, folder_names, filenames)
    #for every directory in the path, starting with the path. Libs must be in THE ONLY
    #subdirectory, hence dirlist[1] for all the following code
    for file in dirlist[1][2]:
        #if file is an xlsx file (which library files should be)
        if(file[-4:]=='xlsx'):
            #read the excel file as a dictionary with key = sheetname
            xl_file = pd.read_excel(dirlist[1][0]+'\\'+file, sheetname=None)

            for key in xl_file.keys():
                #check if the column labels 'part' and 'well' are in this sheet, if so, it's probably a library
                if ('part' in xl_file[key].columns and 'well' in xl_file[key].columns):
                    libs+=[('{}\\{}'.format(dirlist[1][0], file), file[:-4])]

    return sorted(libs)[::-1]

#gets a list of the assembly files present in THE CURRENT PATH
def find_assemblies_RM ():

    #Get name of directory where the current script, along with all other library and assembly files, lives
    currdir = os.getcwd()

    #go through all the items in this directory, files, folders, everything, then save only items that are files
    onlyfiles = [item for item in os.listdir(currdir) if os.path.isfile(currdir + '\\' + item)]

    #initialize list of possible assembly files
    assys = []

    for file in onlyfiles:
        #if file is a csv, which assemblies should be
        if(file[-3:] =='csv'):

            #try to do the following stuff, except pass on an IOError from pd.read_csv
            try:
                assy_csv = pd.read_csv(currdir + '\\' + file)

                #check if the column labels 'promoter' and 'targwell' are in this df, if so, file is probably an assembly
                if ('promoter' in assy_csv.columns and 'targwell' in assy_csv.columns):
                    assys+=[('{}\\{}'.format(currdir, file), file[:-4])]
            except IOError:
                pass
    return sorted(assys)[::-1]

#gets a list of the assembly files present in a path
def find_assemblies_ASS (path):

    #walkr holds generator object that has all the contents of the path directory and subdirectories
    walkr = os.walk(path)
    #convert to a list
    dirlist = list(walkr)

    #initialize list of possible assembly files
    assys = []

    for file in dirlist[0][2]:
        #if file is a csv, which assemblies should be
        if(file[-3:] =='csv'):
            try:
                assy_csv = pd.read_csv(path + '\\' + file)

                #check if the column labels 'promoter' and 'targwell' are in this df, if so, it's probably an assembly
                if ('promoter' in assy_csv.columns and 'targwell' in assy_csv.columns):
                    assys+=[('{}\\{}'.format(path, file), file[:-4])]
            except IOError:
                pass
    return sorted(assys)[::-1]

# user interface for picking a library of parts to use. This list must
# contain the concentration of each part as well as the 384 well location
# of each part.
def pick_parts_library ():

    look = input('Is this: {}\nwhere you want to look for parts libraries? (y/n)   '.format(os.getcwd()))
    if look in ['y', 'Y']:
        pass
    else:
        raise NotImplementedError('Run this script from the directory where your parts library files are')


    print ('Searching for compatible parts libraries...')

    #use function to get all the parts libraries
    partLibList = find_part_libraries_RM()

    #initialize
    pickedlist = ''

    if(len(partLibList) <= 0):
        raise ValueError('could not find any parts libraries :(. Make sure they are in the same directory as this script')
    else:
        print ('Found some libraries')

        for el in range(len(partLibList)):
            #print the number and the short filename from the tuple returned by findPartsLibs()
            print ('[{}]  {}'.format(el,partLibList[el][1]))

        if(len(partLibList) == 1):
            #choose the first and only entry in the libraries list
            #set pickedlist to be the PATH (not the shortened filename) of that library
            pickedlist = partLibList[0][0]
            print ('picked the only one in the list!')
        else:
            userpick = input('type the number of the one you want.   ')
            pickedlist = partLibList[int(userpick)][0]
    openlist = pd.read_excel(pickedlist)

    print ("===================================")
    return openlist

#user interface for picking the assembly to build
def pick_assembly ():

    look = input('Is this: {}\nwhere you want to look for assembly files? (y/n)   '.format(os.getcwd()))
    if look in ['y', 'Y']:
        pass
    else:
        raise NotImplementedError('Run this script from the directory where your assembly files are')

    print ('Searching for compatible assembly files...')

    assyList = find_assemblies_RM()

    #initialize
    pickedlist = ''

    if(len(assyList) <= 0):
        raise ValueError('Could not find any assembly files')

    else:
        print ('I found some assemblies')

        for el in range(len(assyList)):
            print ('[{}]  {}'.format(el,assyList[el][1]))

        if(len(assyList)==1):
            pickedlist = assyList[0][0]
            print ("picked the only one in the list!")

        else:
            userpick = input('type the number of the one you want.   ')
            pickedlist = assyList[int(userpick)][0]

    openlist = pd.read_csv(pickedlist)

    openlist = openlist.dropna(axis=0, how='all')
    print ("===================================")
    return openlist
"""end library and assembly file choosing and opening"""


"""Begin functions for creating the Echo output"""
#Transform the assembly input format into a df of pairs ['part', 'target'] that will get added to later
#Is not called on its own, is called during execution of other functions
def make_part_target_pairs (assembly_df):
    assemblies = assembly_df

    #Get the possible assembly target wells (in the destination PCR plate)
    targwells = np.unique(assemblies['targwell'])

    #Get all the parts that are not the 'comment' and 'targwell' entries
    #(This is general in case you add columns like 'left overhang' and 'right overhang' to accommodate Andy's multiplex assembly method)
    parts = [col for col in list(assemblies.columns) if col not in ['comment', 'targwell']]

    #Initialize dataframe to hold the partwell and target well entries for the whole sheet
    part_target_pairs = pd.DataFrame(columns = ['part', 'target'])

    #Fill the part_target_pairs dataframe with all the partwell and target well pairs
    for targwell in targwells:
        for part in parts:
            dfAdd = pd.DataFrame([[assemblies.loc[assemblies['targwell'] == targwell , part].values[0], targwell]], \
                                 columns = ['part', 'target'])
            part_target_pairs = part_target_pairs.append(dfAdd, ignore_index=True)

    part_target_pairs = part_target_pairs.dropna(axis=0) #drop part_target_pairs with part = NaN

    return part_target_pairs

#Create the list of 'part' 'target' 'volume' values for each part transfer
def part_transfer_list (assembly_df, library_df):

    part_transfers = make_part_target_pairs(assembly_df)
    library = library_df

    #Global variables
    targConc = 4 #nM
    targVol = 4 #uL

    #Loop over all the *unique* parts you want to transfer
    #(each part will be transferred at the same volume no matter which assy it's part of)
    for part in np.unique(part_transfers['part']):

        #Find the part's concentration in the library plate
        conc = library.loc[ library['well'] == part, 'conc (nM)'].values[0] #need .values[0] or you'll get a Series
                                                                            #you can't do math with

        #Calculate transfer vol and make Echo compatible
        transVol = (targConc/conc) * targVol #transVol in uL
        transVol = transVol * 1000 #now in nL

        roundedTo25 = round(transVol / 25) * 25 #echo can only transfer in increments of 25nL, this step rounds to nearest 25nL

        if roundedTo25 == 0:
            roundedTo25 = 25 #better to shoot one drop of part in there instead of having none
                            #even if that means the concentration of that part is not close to 4nM

        #Add the transfer volume to the transfers df that is recording each transfer
        part_transfers.loc[ part_transfers['part'] == part , 'volume' ] = roundedTo25

    return part_transfers

#Create transfers list for water and append it to the bottom of the parts transfers list
def add_water_transfers (part_transfer_list_df, library_df):
    transfers = part_transfer_list_df
    library = library_df

    #Create a transfers dataframe for the water transfers, same format as the part transfers set up in other function
    waterTransfers = pd.DataFrame(columns = ['part', 'target', 'volume'])

    #loop over each destination well and sum the transfer volumes
    for targwell in np.unique(transfers['target']):
        #Get list of volumes going into that destination well
        vols = transfers.loc[transfers['target'] == targwell, 'volume']

        volSum = sum(vols.values) #creates a numpy array of size 1 since vols is a series

        #Find out how much water is needed to get to ~4uL (all volumes handled here are in nL)
        if volSum < 4000:
            waterTrans = round( (4000 - volSum) / 25) * 25
        elif volSum == 4000: #just in case, the other exception of transfer vols exceeding 4000 is already handled in check_vol_errors
            waterTrans = 0

        #Get well that has the water
        waterwell = library.loc[library['part'] == 'WATER', 'well'].values[0] #have to get value[0] otherwise you get a Series
                                                                                #which doesn't work when creating columns later

        dfAdd = pd.DataFrame([[waterwell, targwell, waterTrans]], columns = ['part', 'target', 'volume'])

        waterTransfers = waterTransfers.append(dfAdd, ignore_index=True)

    transfers = transfers.append(waterTransfers, ignore_index=True)

    return transfers

#Create output document for the Echo
def make_echo_csv (part_plus_water_transfers_df):
    transfers = part_plus_water_transfers_df

    #initialize the Echo formatted output dataframe
    out = pd.DataFrame(columns= ['Source Plate Name', 'Source Plate Type', 'Source Well', 'Sample ID', 'Sample Name', \
                                 'Sample Group', 'Sample Comment', 'Destination Plate Name', 'Destination Well', 'Transfer Volume'])

    for idx, row in transfers.iterrows(): #loops over the index and a Series of data for each row, which can be sliced by column name
        out.loc[idx, 'Source Well'] = row['part']
        out.loc[idx, 'Destination Well'] = row['target']
        out.loc[idx, 'Transfer Volume'] = row['volume']

    out[['Source Plate Name', 'Source Plate Type', 'Destination Plate Name']] = ['Source[1]', '384PP_AQ_BP', 'Destination[1]']

    return out
"""end functions for making echo-formatted output"""



"""Begin functions for checking things in the process of making the echo output"""
#Check if requested parts are in the library file
def check_if_in_lib (assembly_df, library_df):

    part_target_pairs = make_part_target_pairs(assembly_df)

    liberrs = []

    for part in np.unique(part_target_pairs['part']):
        if part not in library_df['well'].values:
            liberrs.append(part)
    if liberrs:
        raise ValueError('***The requested parts in wells {} are not in the library file***'.format(liberrs))
    else:
        return None

#Checks for total transfer volumes that exceed 4uL
def check_vol_errors (part_transfer_list_df):
    transfers = part_transfer_list_df

    #Initialize the list of destination wells where transfers exceed 4uL
    volerrs = []

    #loop over each destination well and sum the transfer volumes
    for targwell in np.unique(transfers['target']):
        vols = transfers.loc[transfers['target'] == targwell, 'volume']

        #check if all transfers exceed 4uL (all volumes handled here are in nL)
        if sum(vols.values) > 4000:
            volerrs.append(targwell)

    #if the list of destination well errors has entries (is True), raise an error that lists them
    if volerrs:
        raise ValueError('***Sum of transfer volumes into destination wells {} is greater than 4uL***'.format(volerrs))
    else:
        return None

#Check the library file to see if there is enough volume of each part
#available to complete the requested transfers
def check_enough_vol (part_plus_water_transfers_df, library_df):
    transfers = part_plus_water_transfers_df
    library = library_df

    volErr = []

    for part in np.unique(transfers['part']):
        vols = transfers.loc[transfers['part'] == part, 'volume'] #in nL

        totalTrans = sum(vols) / 1000 #total transferred volume, in uL

        currVol = library.loc[library['well'] == part, 'Vol (uL) in plate'].values #need to get array instead of series
                                                                                #otherwise following if statement can't
                                                                                #be evaluated since truth table of Series
                                                                                #can't be determined.

        #leave a buffer zone. Echo can't transfer less than 15. Give 2uL buffer here
        if (currVol - totalTrans) < 17:
            volErr.append(part)

        #find water well
        waterwell = library.loc[library['part'] == 'WATER', 'well'].values[0]

    #if volErr has entries and waterwell is one of them
    if volErr and (waterwell in volErr):

        #if there is more than 1 entry in volErr, meaning there are part errors beyond the waterwell.
        if len(volErr) > 1:

            #get index of the water well in volErr
            k = volErr.index('A10')

            #construct list that just has the remaining part errors
            parterrs = volErr[:k] + volErr[(k + 1):]

            raise ValueError('***Part wells {} do not have enough volume in them. Additionally, water well {} does not have enough volume***'\
                  .format(parterrs, waterwell))

        #if volErr has 1 element (just the water well) (less than one is impossible due to top level if statement)
        else:
            raise ValueError('***The water well: {}, does not have enough volume in it***'.format(waterwell))

    #if volErr has entries but water well is NOT one of them
    elif volErr:
        raise ValueError('***Part wells {} do not have enough volume in them***'.format(volErr))

    #there are no volErr
    else:
        return None

#Check the final output document to make sure the total transfer volumes are
#4uL
def check_if_final_vols_ok (output_df):

    desired_total_volume = 4000 #in nL, this is 4uL

    final_vol_errs = []

    for targwell in np.unique(output_df['Destination Well']):

        vols = output_df.loc[ output_df['Destination Well'] == 'A4', 'Transfer Volume' ]

        if sum(vols) != desired_total_volume:
            final_vol_errs.append(targwell)

    if final_vol_errs:
        raise ValueError('***The wells {} will have more than 4uL (parts + water) transferred to them***'.format(final_vol_errs))
    else:
        return None
"""end functions for checking things during echo output creation"""



"""Functions for updating input library to reflect volumes used in assembly"""
# Use the final output sheet to subtract volume from the library part volumes
# to keep track of how much is in each well
# ***You have to be careful with this function, if you regenerate an output sheet for testing
# or just out of neuroticism, running this function each time will subtract from the library
# volumes, even though an assembly has not been done. Only use this function when an assembly
# has actually been done!***
def update_lib_vols (want_to_run, output_df, library_df):
    output = output_df
    library = library_df

    #want_to_run is a bool that determines if the function should run and actually update the library
    if want_to_run:
        for part in np.unique(output['Source Well']):
            vols = output.loc[output['Source Well'] == part, 'Transfer Volume'] #in nL

            totalTrans = sum(vols) / 1000 #total transferred volume, in uL

            currVol = library.loc[library['well'] == part, 'Vol (uL) in plate']

            newVol = currVol - totalTrans

            #set the volume in the plate to the new volume
            library.loc[library['well'] == part, 'Vol (uL) in plate'] = newVol

        return library

    else:
        return None
"""end library update functions"""



"""Main running block"""

def main():
    #first you need to get your library and desired assembly
    assy = pick_assembly()
    lib = pick_parts_library()

    #then you should check to see if the assembly parts are in the library
    check_if_in_lib(assy, lib)

    #then begin by making the part-well / target-well pair assignments
    #and calculate the volume to shoot
    #(e.g. 550uL of part in well A1 will get shot into target well A4)
    part_trans = part_transfer_list(assy, lib)

    #now that you have calculated the volumes of each part to transfer,
    #check to see if the total transferred volume of PARTS alone is more than 4uL
    check_vol_errors(part_trans)

    #since all part transfers sum to 4000nL or less, you should fill the target
    #wells with water up to 4000nL
    part_water_trans = add_water_transfers(part_trans, lib)

    #now that you have a full set of transfers with parts and water,
    #check the library to see if there's enough volume of each thing
    #to do the requested transfers
    check_enough_vol (part_water_trans, lib)

    #now create the df that is formatted correctly for the Echo Plate Reformat
    #software to read it
    output = make_echo_csv(part_water_trans)

    #final neurotic check, make sure the output df will not transfer more than
    #4000nL into any given target well
    check_if_final_vols_ok(output)

    output.to_csv(os.getcwd() + '\\output.csv', index=False)

    print('I did the whole thing, your Echo pick list file is called "output.csv"')

    return None


if __name__ == '__main__':
    main()
