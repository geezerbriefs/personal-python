"""
### Update GGA Parts Library File Script ###

This script is designed to take in a .csv file containing a physically completed
Echo pick list protocol generated for GGA cloning using MoCloAssy.py and a GGA
parts plate library file (.xlsx). It will look at the Echo transfer protocol and
update the given parts library file by subtracting the amount transfered during
the protocol from the appropriate well's "vol in plate" field. It then rewrites
the original library file with the updated one. Ideally, this will let you know
when you are running low on a particular part, the checking functions in
MoCloAssy.py will raise errors if too little volume is left of a desired part.

Instructions:
*Use MoCloAssy.py to generate an "output.csv", save this file more descriptively
    somewhere
*Run the transfer with the Echo using your saved pick list file from above step
*Run this script, giving it the pick list you just ran and your library file
*Your library is now updated

Created: 10/07/2017

Updated: 10/09/2017

Update Notes: Doesn't yet write over the original library. Possible add function
to just append new sheets to the library where sheet name is the time of update.
Added a verification step "do you really want to update?"

"""

import pandas as pd
import numpy as np
import os
import string


"""Functions for updating input library to reflect volumes used in assembly"""
# Use the final output sheet to subtract volume from the library part volumes
# to keep track of how much is in each well
# ***You have to be careful with this function, if you regenerate an output sheet for testing
# or just out of neuroticism, running this function each time will subtract from the library
# volumes, even though an assembly has not been done. Only use this function when an assembly
# has actually been done!***
def update_lib_vols (pick_list_df, library_df):
    output = pick_list_df
    library = library_df

    for part in np.unique(output['Source Well']):
        vols = output.loc[output['Source Well'] == part, 'Transfer Volume'] #in nL

        totalTrans = sum(vols) / 1000 #total transferred volume, in uL

        currVol = library.loc[library['well'] == part, 'Vol (uL) in plate']

        newVol = currVol - totalTrans

        #set the volume in the plate to the new volume
        library.loc[library['well'] == part, 'Vol (uL) in plate'] = newVol

    return library

#verify the user wants to udpate their library sheet, gives option to correct a mistake
def check_before_update():
    YorN = input('Do you really want to update this library with this assembly? (y/n)   ')

    if YorN in ['Y', 'y']:
        pass
    elif YorN in ['N', 'n']:
        raise ValueError('Update procedure aborted')
    else:
        raise ValueError('I do not recognize this input, procedure aborted')

    return None

"""end library update functions"""


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

#gets a list of the assembly files present in THE CURRENT PATH
def find_pick_lists ():

    #Get name of directory where the current script, along with all other library and assembly files, lives
    currdir = os.getcwd()

    #go through all the items in this directory, files, folders, everything, then save only items that are files
    onlyfiles = [item for item in os.listdir(currdir) if os.path.isfile(currdir + '\\' + item)]

    #initialize list of possible assembly files
    pls = []

    for file in onlyfiles:
        #if file is a csv, which pick lists should be
        if(file[-3:] =='csv'):

            #try to do the following stuff, except pass on an IOError from pd.read_csv
            try:
                pick_csv = pd.read_csv(currdir + '\\' + file)

                #check if the column labels from a complete pick list are in this df, if so, file is probably a pick list
                full_pl_cols = ['Source Plate Name', 'Source Plate Type', 'Source Well',
                'Sample ID', 'Sample Name', 'Sample Group', 'Sample Comment',
                'Destination Plate Name', 'Destination Well', 'Transfer Volume']

                if (all(x in full_pl_cols for x in pick_csv.columns)):
                    pls += [('{}\\{}'.format(currdir, file), file[:-4])]
            except IOError:
                pass
    return sorted(pls)[::-1]

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
            userpick = input('type the number of the one you used to make your assembly.   ')
            pickedlist = partLibList[int(userpick)][0]
    openlist = pd.read_excel(pickedlist)

    print ("===================================")
    return openlist

#user interface for picking the assembly to build
def pick_pick_list ():

    look = input('Is this: {}\nwhere you want to look for pick list files? (y/n)   '.format(os.getcwd()))
    if look in ['y', 'Y']:
        pass
    else:
        raise NotImplementedError('Run this script from the directory where your pick list files are')

    print ('Searching for compatible pick lists...')

    plList = find_pick_lists()

    #initialize
    pickedlist = ''

    if(len(plList) <= 0):
        raise ValueError('Could not find any pick lists')

    else:
        print ('I found some lists')

        for el in range(len(plList)):
            print ('[{}]  {}'.format(el,plList[el][1]))

        if(len(plList)==1):
            pickedlist = plList[0][0]
            print ("picked the only one in the list!")

        else:
            userpick = input('type the number of the one you ran on the Echo.   ')
            pickedlist = plList[int(userpick)][0]

    openpl = pd.read_csv(pickedlist)

    openpl = openpl.dropna(axis=0, how='all')
    print ("===================================")
    return openpl
"""end library and assembly file choosing and opening"""


"""Begin block of functions for writing the updated dataframe"""
def write_to_xlsx (updated_lib_df):

    """I don't really understand what a writer object is for this xlsxwriter stuff
    I think the writer object is like a set of formatting instructions for dataframes,
    which we use to convert the df to an xlsx document. Why I can modify the writer
    object after I have alread converted the df to xlsx is a mystery to me.
    It works though """


    #create ExcelWriter object to handle creating your new library file as .xlsx
    new_file_name = 'new updated lib.xlsx'
    writer = pd.ExcelWriter(new_file_name, engine='xlsxwriter')

    #convert the dataframe to an xlsxwriter excel object
    updated_lib_df.to_excel(writer, sheet_name='Sheet1', index=False)

    #Get the xlsxwriter worksheet object.
    worksheet = writer.sheets['Sheet1']

    #Use the set of 26 uppercase letters, zero-indexed, to get the excel column
    #for the right most column in the updated library df
    r_most_col = string.ascii_uppercase[len(updated_lib_df.columns) - 1]

    #Set an autofilter with no conditions, the saved .xslx file will have the filter
    #already on. Nice!
    worksheet.autofilter('A1:{}1'.format(r_most_col)) #can automatically deal with
                                                      #libraries with columns up to
                                                      #'Z', no combinatorial 'AB' etc

    #Close the Pandas Excel writer and output the Excel file.
    writer.save()

    print('I saved your updated library file as: {}'.format(new_file_name))

    return None

"""end writing dataframe functions"""



def main():
    library_used = pick_parts_library()
    pl_used = pick_pick_list()

    check_before_update()

    updated_library = update_lib_vols (pl_used, library_used)

    write_to_xlsx (updated_library)

    return None

if __name__ == '__main__':
    main()
