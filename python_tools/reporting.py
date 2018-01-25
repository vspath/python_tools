import os
import pprint
import pandas as pd
import re


def find_files(base_path = os.getcwd(), file_extension=None):

    if file_extension:
        if not file_extension.startswith("."):
            file_extension = "." + file_extension

        files = [os.path.join(root, name)
                 for root, dirs, files in os.walk(base_path)
                 for name in files
                 if name.endswith(file_extension)]

    else:
        files = [os.path.join(root, name)
                 for root, dirs, files in os.walk(base_path)
                 for name in files]

    return files


def create_file_overview(base_path=os.getcwd()):

    files = find_files(base_path=base_path, file_extension="html")

    table_dict = {}
    #table = pd.DataFrame()
    #overview['date']
    #overview['html'] #plots
    #overview['notebooks']
    #overview['data']

    table_dict["date"] = []
    table_dict["scenario"] = []

    #table_dict["html"] = []
    html_files = []

    for file in files:
        path_split = file.split("/")
        #table_dict["date"].extend([s for s in path_split if re.search("^\d\d.*$", s)])

        # check if several files have the same extension

        # get date and idx of date in path split list
        for idx, s in enumerate(path_split):
            if re.search("^\d\d.*$", s):
                # get date of test run from folder name
                table_dict["date"].append(s)
                rel_path = "/".join(path_split[idx+1:])

                # get first two folder names of relative path after date folder to a file
                table_dict["scenario"] = "/".join(rel_path.split("/")[0:2])



        html_files.extend([s for s in path_split if s.endswith(".html")])


        #scenario = [s for s in path_split if re.search()]

    table = pd.DataFrame.from_dict(table_dict)
    return(table_dict)

f = find_files("/Users/VeSpa/Documents/20180123_162837/tests/temperature-get_adc_dependent_temperature_values_with_cts[001-18500]/analysis_output", "html")
#pprint.pprint(f)

t = create_file_overview("/Users/VeSpa/Documents/")
#pprint.pprint(t)


