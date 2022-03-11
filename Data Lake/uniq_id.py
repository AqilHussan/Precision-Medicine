'''
Convert RID, ID to PTID as the unique identifier.
SITEID could be used as a categorical variable later on. 
Feb 05, 2022
'''


import pandas as pd
import numpy as np
import glob 
import os

# files accessed from the local file system, will change to HDFS as and when the storage layer of data lake is completed.
# Change required such that any .csv in the directory and its subdirectories is changed as well.
file_path = "/home/akash/datalake/raw_data/*.csv"
save_path = "/home/akash/datalake/processed_data/"

roster = pd.read_csv('/home/akash/ROSTER.csv')

ptid_dict = dict(zip(roster['RID'], roster['PTID']))
#print(ptid_dict)

for fname in glob.glob(file_path):
     df = pd.read_csv(fname)

     file_name = os.path.basename(fname)     
             
     if 'PTID' in df.columns:
          df = df.drop('RID', 1)
          df = df.drop('ID', 1)
          df.to_csv(save_path+file_name, index = False)

     
     else:
          df = df.drop('ID', 1)
          df['PTID'] = df['RID'].map(ptid_dict)
          df = df.drop('RID', 1)
          df.to_csv(save_path+file_name, index = False)

