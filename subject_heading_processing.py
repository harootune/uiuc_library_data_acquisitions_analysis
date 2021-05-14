import string
import re
import collections

import pandas as pd

from call_number_processing import dataframe_from_data_folder

# globals
MAX_SUBDIVISIONS = 0


def get_subject_heading_counts(record_df: pd.DataFrame):
    heading_list = []

    def per_row_heading_count(row):
        if pd.isna(row["Subjects"]):
            return 0
        else:
            headings = row["Subjects"].split(";")
            
            for heading in headings:
                
                heading = heading.strip().strip('.')
                divisions = heading.split("--")

                clean_heading = divisions[0]
                
                i = 0
                while i < MAX_SUBDIVISIONS and (i + 1) < len(divisions):
                    clean_heading +=  ("--" + divisions[i + 1])
                    i += 1
                
                heading_list.append(clean_heading)  # SIDE-EFFECT HERE

            return len(headings)
    
    record_df.apply(per_row_heading_count, axis=1)
    
    return collections.Counter(heading_list)
        

def main(result_file_name: str):
    record_df = dataframe_from_data_folder()

    heading_frequency_counter = get_subject_heading_counts(record_df)

    heading_frequency_df = pd.DataFrame.from_dict(heading_frequency_counter, orient="index")

    heading_frequency_df = heading_frequency_df.rename({0: "count"}, axis=1)

    heading_frequency_df = heading_frequency_df.sort_values("count", ascending=False)

    with open(result_file_name, mode="w") as outfile:
        pd.set_option('display.max_rows', None)
        print(heading_frequency_df, file=outfile)

if __name__ == "__main__":
    result_file_name = "unique_subject_headings.txt"
    main(result_file_name)