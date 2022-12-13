import dm_extract_bon_data
import rewe_extract_bon_data
import lidl_extract_bon_data
import os
import pandas as pd

LIDL_SUM = lidl_extract_bon_data.LIDL_SUM
REWE_SUM = []
DM_SUM = []

path_rewe = 'Rewe/'
path_lidl = 'lidl/'
path_dm = 'dm/'

PATHS = [path_rewe, path_lidl, path_dm]
#PATHS = 'bon_data/'

def combine_files(paths):
    complete_rewe_files = []
    complete_dm_files = []
    complete_lidl_files = []

    """
    retrives all the filenames of the bons
    """
    for path in paths:
        for root, dir_names, file_names in os.walk(path):
            for file in file_names:
                if 'REWE' in file:
                    complete_rewe_files.append(os.path.join(root, file))
                elif '.png' in file:
                    complete_lidl_files.append(os.path.join(root, file))
                elif 'dm-eBon' in file:
                    complete_dm_files.append(os.path.join(root, file))

    """
    creates one dataframe out of a list of dataframes for each grocery store. Additionally it adds all the final sums to a global except for LIDL
    """
    complete_dm_dfs = []
    for files in complete_dm_files:
        final_df = dm_extract_bon_data.executer(files)
        complete_dm_dfs.append(final_df[0])
        DM_SUM.append(final_df[1])
    if len(complete_dm_dfs) > 1:
        final_dm_df = pd.concat(complete_dm_dfs, ignore_index = True)
    else:
        final_dm_df = complete_dm_dfs[0]

    complete_lidl_dfs = []
    for files in complete_lidl_files:
        final_df = lidl_extract_bon_data.executer(files)
        complete_lidl_dfs.append(final_df[0])
        #LIDL_SUM.append(final_df[1])
    if len(complete_lidl_dfs) > 1:
        final_lidl_df = pd.concat(complete_lidl_dfs, ignore_index = True)
    else:
        final_lidl_df = complete_lidl_dfs[0]

    complete_rewe_dfs = []
    for files in complete_rewe_files:
        final_df = rewe_extract_bon_data.executer(files)
        complete_rewe_dfs.append(final_df[0])
        REWE_SUM.append(final_df[1])
    if len(complete_rewe_dfs):
        final_rewe_df = pd.concat(complete_rewe_dfs, ignore_index = True)
    else:
        final_rewe_df = complete_rewe_dfs[0]

    """
    combines all the dataframes to one dataframe
    """
    final_df = pd.concat([final_dm_df, final_lidl_df, final_rewe_df], ignore_index = True)
    return final_df