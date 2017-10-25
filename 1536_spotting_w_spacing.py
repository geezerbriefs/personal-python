import pandas as pd
import os

class plate1536:
    """Holds all the column and row values about 1536 well plates"""

    #all the rows in a 1536 well plate (32 of them)
    rows = ['A','B','C','D','E','F','G','H','I','J','K','L',\
               'M','N','O','P','Q','R','S','T','U','V','W','X',\
               'Y','Z','AA','AB','AC','AD','AE','AF']

    #make a dict so each row name is accessible by a number
    row_dict = {}

    for i in range(len(rows)):
        row_dict[i] = rows[i]

    #all the columns in a 1563 well plate (48 of them)
    columns = [i+1 for i in range(48)]


def split_well_name (well_name):
    """Splits a well name into letter and number parts"""

    letters = well_name.rstrip('0123456789')

    nums = well_name.lstrip(letters)


    #Do some checks to make sure it's a well name in for the format letter-letter-#-#
    if len(nums) == 0:
        raise ValueError('Something is wrong with your input, I cannot find a row number')


    for i in '0123456789':
        if i in letters:
            raise ValueError('Something is wrong with your input, I think there is a number in your column letter.')

    for j in nums:
        if j not in '0123456789':
            raise ValueError('Something is wrong with your input, I think there is a letter in your row number.')

    return letters, nums


def get_corners ():

    """User inputs well names, split the well names into letters and numbers
    Then output each well name as a tuple ('letters', 'numbers')"""

    top_l = input("Input the top left well of this spotting region (A1 to AF48):   ")

    bot_r = input("Input the bottom right well of this spotting region (A1 to AF48):   ")

    top_left = split_well_name(top_l)

    bottom_right = split_well_name(bot_r)

    return top_left, bottom_right



def check_orient (tuple_top_L, tuple_bottom_R):
    """Checks to make sure the top left and bottom right wells are in the
    correct orientations relative to each other"""

    #get the plate columns from the plate class
    columns = plate1536.columns

    #get the plate rows from the plate class
    rows = plate1536.rows

    #check if bottom_R is actually below top_L
    if rows.index(tuple_top_L[0]) > rows.index(tuple_bottom_R[0]):
        raise ValueError('Your bottom right well is ABOVE your top left well')

    #check if bottom_R is actually to the right of top_L
    if columns.index(int(tuple_top_L[1])) > columns.index(int(tuple_bottom_R[1])):
        raise ValueError('Your bottom right well is LEFT of your top left well')

    return None


def create_region_w_spacing (tuple_top_L, tuple_bottom_R):

    """User inputs desired spacing between spots. Uses column and row from top left
    well location to create 2 lists of columns and rows that increment by the
    desired number of spaces between them. These can be combined to make a rectangular
    grid with the desired spacing in between each spot in x and y directions."""

    spacing = int(input ('How many well spaces do you want between each spot?   '))


    #get the plate column numbers from the plate class
    columns = plate1536.columns
    #get the plate rows from the plate class
    rows = plate1536.rows

    ###Begin creating list of columns to use###

    #initialize and use next
    curr_col_idx = columns.index(int(tuple_top_L[1]))

    #set left most column to use as the column given by user in top_left
    col_idxs_to_shoot = [curr_col_idx]

    #loop checks the NEXT column that will be produced by moving right
    #by (spacing + 1). If that is beyond the right-most border set by
    #the well region definitions, then it will stop, containing all
    #column choices within the left and right bounds
    while (curr_col_idx + spacing + 1) <= columns.index(int(tuple_bottom_R[1])):

        curr_col_idx += (spacing + 1)

        col_idxs_to_shoot.append(curr_col_idx)

    ###The list of indices in plate1536.columns to use is now set###


    ###Begin creating list of rows to use###

    #initialize and use next
    curr_row_idx = rows.index(tuple_top_L[0])

    #set top most row to use as the row given by user in top_left
    row_idxs_to_shoot = [curr_row_idx]

    #loop checks the NEXT row that will be produced by moving down
    #by (spacing + 1). If that is beyond the bottom-most border set by
    #the well region definitions, then it will stop, containing all
    #row choices within the top and bottom bounds
    while (curr_row_idx + spacing + 1) <= rows.index(tuple_bottom_R[0]):

        curr_row_idx += (spacing + 1)

        row_idxs_to_shoot.append(curr_row_idx)

    ###The list of indices in plate1536.rows to use is now set###


    #get all the columns you want to use as STRINGS
    col_strs = []
    for i in col_idxs_to_shoot:
        col_strs += [ str(plate1536.columns[i]) ] #have to have extra list brackets to avoid python interpreting a string 'FFF' as
                                            #a list ['F', 'F', 'F'] and adding 3 items instead of 'FFF'

    #get all the rows you want to use as STRINGS
    row_strs = []
    for i in row_idxs_to_shoot:
        row_strs += [ plate1536.row_dict[i] ]#have to have extra list brackets to avoid python interpreting a string 'FFF' as
                                            #a list ['F', 'F', 'F'] and adding 3 items instead of 'FFF'


    return row_strs, col_strs


def well_list_from_region (row_strs, col_strs):

    """Makes a single list of wells of format 'AA##' that represent the destination
    well locations to be shot by the echo"""

    well_pos_list = []
    for i in row_strs:
        for j in col_strs:
            well_pos_list += [ i + j ]#have to have extra list brackets to avoid python interpreting a string 'FFF' as
                                     #a list ['F', 'F', 'F'] and adding 3 items instead of 'FFF'

    return well_pos_list


def add_source_and_vol (well_list):

    """Ask the user where the shots should come from, assumed to be the same for
    all shots in the region. Also asks how much volume to shoot for each spot,
    also assumed to be the same for all"""

    source = input('From which source well will you be shooting in this region?   ')

    vol = int(input('How much volume (nL) do you want to shoot in this region?  '))

    if vol%25 != 0: #modulo needs to be 0 for multiple of 25
        raise ValueError('This number is not compatible with the Echo, please enter a multiple of 25 nL.')

    return (source, vol, well_list)



def make_echo_csv (list_of_region_tuples):

    """Compiles all the information into a dataframe in correct Echo input format"""

    #initialize the Echo formatted output dataframe
    out = pd.DataFrame(columns= ['Source Plate Name', 'Source Plate Type', 'Source Well', 'Sample ID', 'Sample Name', \
                                 'Sample Group', 'Sample Comment', 'Destination Plate Name', 'Destination Well', 'Transfer Volume'])

    idx = 0 #have to use a counter because we go through multiple lists and can't return to idx=0 each time
    #there may be a list of region tuples with source wells, volumes, dest wells
    for region in list_of_region_tuples:
        #for each well location to be shot from the current region
        for well in region[2]:
            #add the dest well
            out.loc[idx, 'Destination Well'] = well
            #Add the source well and transfer volume for that region
            out.loc[idx, ['Source Well', 'Transfer Volume']] = [region[0], region[1]]
            idx += 1

    #Set the unchanging names for the dataframe
    out[['Source Plate Name', 'Source Plate Type', 'Destination Plate Name']] = ['Source[1]', '384PP_AQ_BP', 'Destination[1]']

    return out


def main ():
    more = 'y'

    all_infos = []
    while more in ['y', 'Y']:
        tl, br = get_corners()

        check_orient (tl, br)

        row, col = create_region_w_spacing (tl, br)

        wells = well_list_from_region (row, col)

        region_info = add_source_and_vol (wells)

        all_infos.append(region_info)

        more = input('Is there another region into which you would like to shoot spots? (y/n)   ')

    output = make_echo_csv (all_infos)

    output.to_csv(os.getcwd() + '\\RM_spotting_output.csv', index=False)

    print("Your pick list is saved in the working directory as 'RM_spotting_output.csv' ")

    return None

if __name__ == '__main__':
    main()
