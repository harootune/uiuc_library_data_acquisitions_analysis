import string
import re
import os

import pandas as pd
import pycallnumber as pcn
from pycallnumber.units.callnumbers import Dewey, LC, SuDoc, LcClass, DeweyClass ,Local

PREFIX_KEYWORDS_PATTERN = '(CD|ER|DVD|ROM|DOC|Q\.|HARDDRIVE|KIT|GUIDE|DISC|USGS|FICHE|EPA|DSK|COMD|STAT|NTIS)'


def dataframe_from_data_folder(data_directory="data"):
    
    frame_list = []

    for filename in os.listdir(data_directory):

        try:
            frame_list.append(pd.read_excel(data_directory + "/" + filename))
        except FileNotFoundError:
            continue
    
    if len(frame_list) > 0:
        return pd.concat(frame_list)
    else:
        return None


def find_local_prefix(call_number, split=" "):

    stringified_call_number = str(call_number)
    split_call_number = stringified_call_number.split()

    if split_call_number:
        prefix = split_call_number[0]
    else:
        prefix = ''

    return prefix


def correct_local_prefix(row, split=" ", target_col="Call Number", target_col_type="call_number_type"):

    if row[target_col_type] == "L" and row[target_col]:

        split_call_number = row[target_col].split(split)

        if re.match(PREFIX_KEYWORDS_PATTERN, split_call_number[0]):
            if len(split_call_number) == 1:
                return row[target_col]
            else:
                return " ". join(split_call_number[1:])
        else:
            return row[target_col]

    else:
        return row[target_col]


def check_call_number_type(call_number):

    if pd.isna(call_number) or not call_number:
        return "N"
    else:
        parsed_call_number = pcn.callnumber(call_number)
        
        if isinstance(parsed_call_number, Dewey) or isinstance(parsed_call_number, DeweyClass):
            return "D"
        elif isinstance(parsed_call_number, LC) or isinstance(parsed_call_number, LcClass):
            return "C"
        elif isinstance(parsed_call_number, SuDoc):
            return "S"
        elif isinstance(parsed_call_number, Local):
            return "L"
        else:
            return "N"


if __name__ == "__main__":

    def progressive_call_number_correction(df, split_symbols):
        
        i = 0
        last_col_name = "Call Number"
        last_col_name_type = "call_number_type"

        while (i < len(split_symbols)):
            print(i)

            current_col_name = "corrected_call_number" + str(i + 1)
            current_col_name_type = "corrected_call_number_type" + str(i + 1)

            df[current_col_name] =  df.apply(correct_local_prefix, axis=1, target_col=last_col_name, target_col_type=last_col_name_type)
            df[current_col_name_type] = df[last_col_name].map(check_call_number_type)

            last_col_name = current_col_name
            last_col_name_type = current_col_name_type
            i += 1
        
        return df
    
    def prefix_report(df, number_col, type_col):
        prefixes = df[df[type_col] == "L"][number_col].map(find_local_prefix)
        print(prefixes.unique())
    
    def type_value_report(df, type_col):
        print(df[type_col].value_counts())

    print(pcn.callnumber("3"))
    print(check_call_number_type("378.02"))

    alma_df = dataframe_from_data_folder()
    alma_df = alma_df[alma_df["Term"] != "Term"]
    alma_df["call_number_type"] = alma_df["Call Number"].map(check_call_number_type)
    split_symbols = [" ", "."]
    alma_df = progressive_call_number_correction(alma_df, split_symbols)
    
    number_col = "Call Number"
    type_col = "call_number_type"
    type_value_report(alma_df, type_col)
    prefix_report(alma_df, number_col, type_col)

    for i in range(len(split_symbols)):
        number_col = "corrected_call_number" + str(i + 1)
        type_col = "corrected_call_number_type" + str(i + 1)
        type_value_report(alma_df, type_col)
        prefix_report(alma_df, number_col, type_col)

    pd.set_option('display.max_rows', None)

    with open("callnumbers.txt", mode="w") as outfile:

        final_col_name = "corrected_call_number" + str(len(split_symbols))
        final_col_name_type = "corrected_call_number_type" + str(len(split_symbols))

        print(alma_df[[final_col_name, final_col_name_type]], file=outfile)
