#!/usr/bin/env python
# coding: utf-8

# ### Unify CSVs

# In[ ]:


import pandas as pd
import os
print('unify start')


# In[ ]:


# Directory containing your CSV files
directory = 'outputs/chain_data'
output_file = 'outputs/all_chain_activity_by_day_gs.csv'

# Create an empty DataFrame to store combined data
combined_df = pd.DataFrame()

# Loop through the directory and append each matching CSV to the DataFrame
for filename in os.listdir(directory):
    if ('chain_activity_by_day_gs' in filename and filename.endswith('.csv')) & (filename != 'opchain_activity_by_day_gs.csv'):
        print(filename)
        filepath = os.path.join(directory, filename)
        temp_df = pd.read_csv(filepath)
        combined_df = pd.concat([combined_df, temp_df], ignore_index=True)
        temp_df = None # Free up Memory

# Save the combined DataFrame to a single CSV file
combined_df['dt'] = pd.to_datetime(combined_df['dt'])
combined_df = combined_df.rename(columns={'chain':'chain_gs'})
combined_df.to_csv(output_file, index=False)
print('All CSVs have been combined and saved.')
# print(combined_df.columns)


# In[ ]:


# Join to Defillama
print('start dfl merge')
# Load the TVL data
tvl_data_path = '../other_chains_tracking/outputs/dfl_chain_tvl.csv'
tvl_df = pd.read_csv(tvl_data_path)
tvl_df = tvl_df.rename(columns={'date':'dt','chain':'chain_dfl'})
# Remove Partial Days
tvl_df['dt'] = pd.to_datetime(tvl_df['dt'])
# tvl_df = tvl_df[tvl_df['dt'].dt.time == pd.Timestamp('00:00:00').time()]
# # Cast to date format
# tvl_df['dt'] = tvl_df['dt'].dt.date
# print(tvl_df.columns)



# In[ ]:


print(combined_df[['chain_gs','chain_name','dt','num_raw_txs']].sample(1))
print(tvl_df[['chain_dfl','chain_name','dt','tvl']].sample(1))


# In[ ]:


# Perform a left join on 'chain_name' and 'dt'
merged_df = pd.merge(combined_df, tvl_df, on=['chain_name','dt'], how='left')

# Save the merged DataFrame to a new CSV file
output_path = 'outputs/all_chain_data_by_day_combined.csv'
merged_df.to_csv(output_path, index=False)

print('Merged data has been saved to:', output_path)


# ### Import to GSheets

# In[ ]:


# import gspread
# from oauth2client.service_account import ServiceAccountCredentials


# In[ ]:


# # Google Sheets credentials and scope
# scope = ['https://www.googleapis.com/auth/spreadsheets']
# credentials = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials.json', scope)
# client = gspread.authorize(credentials)

# # Open the Google Sheet and select the tab
# sheet = client.open('Name_of_Your_Sheet').worksheet('Transaction Data')

# # Clear existing data in the sheet
# sheet.clear()

# # Read the combined CSV file
# data_df = pd.read_csv(output_file)

# # Convert DataFrame to a list of lists, where each sublist is a row in the DataFrame
# data_list = data_df.values.tolist()

# # Insert column headers as the first row
# data_list.insert(0, data_df.columns.tolist())

# # Update the sheet with the new data
# sheet.update('A1', data_list)

# print('Google Sheet has been updated with new data.')

