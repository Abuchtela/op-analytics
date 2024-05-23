#!/usr/bin/env python
# coding: utf-8

# In[ ]:


print('get filtered deployers')
import sys
sys.path.append("../helper_functions")
import duneapi_utils as d
import flipside_utils as f
import clickhouse_utils as ch
sys.path.pop()

import numpy as np
import pandas as pd
from datetime import timedelta
import os
import clickhouse_connect as cc


# In[ ]:


ch_client = ch.connect_to_clickhouse_db() #Default is OPLabs DB


# In[ ]:


flipside_configs = [
        {'blockchain': 'blast', 'name': 'Blast', 'layer': 'L2', 'trailing_days': 365}
]
clickhouse_configs = [
        {'blockchain': 'metal', 'name': 'Metal', 'layer': 'L2', 'trailing_days': 365},
        {'blockchain': 'mode', 'name': 'Mode', 'layer': 'L2', 'trailing_days': 365},
        {'blockchain': 'bob', 'name': 'BOB (Build on Bitcoin)', 'layer': 'L2', 'trailing_days': 365},
        {'blockchain': 'fraxtal', 'name': 'Fraxtal', 'layer': 'L2', 'trailing_days': 365},
]


# In[ ]:


# # Run Flipside - TODO: Build Deployer Query (tbd if it will run)
# print('     flipside runs')
# flip_dfs = []
# with open(os.path.join("inputs/sql/flipside_bychain.sql"), "r") as file:
#                         og_query = file.read()

# for chain in flipside_configs:
#         print(     'flipside: ' + chain['blockchain'])
#         query = og_query
#         #Pass in Params to the query
#         query = query.replace("@blockchain@", chain['blockchain'])
#         query = query.replace("@name@", chain['name'])
#         query = query.replace("@layer@", chain['layer'])
#         query = query.replace("@trailing_days@", str(chain['trailing_days']))
        
#         df = f.query_to_df(query)

#         flip_dfs.append(df)

# flip = pd.concat(flip_dfs)
# flip['source'] = 'flipside'
# flip['dt'] = pd.to_datetime(flip['dt']).dt.tz_localize(None)
# flip = flip[['dt','blockchain','name','layer','num_qualified_txs','source']]


# In[ ]:


# Run Dune
print('     dune runs')
dune_df = d.get_dune_data(query_id = 3753590, #https://dune.com/queries/3753590
    name = "dune_evms_qualified_txs",
    path = "outputs"
)
dune_df['source'] = 'dune'
dune_df['created_dt'] = pd.to_datetime(dune_df['created_dt']).dt.tz_localize(None)
dune_df = dune_df[['created_dt','blockchain','creator_address']]


# In[ ]:


dune_meta_df = d.get_dune_data(query_id = 3445473, #https://dune.com/queries/3445473
    name = "dune_evms_info",
    path = "outputs",
    num_hours_to_rerun = 12
)
cols = ['blockchain','name','layer']
dune_df = dune_df.merge(dune_meta_df[cols], on='blockchain',how='inner')

dune_df.sample(5)


# In[ ]:


# # Run Clickhouse - TODO: Build Deployer Query (tbd if it will run)
# print('     clickhouse runs')
# ch_dfs = []
# with open(os.path.join("inputs/sql/goldsky_bychain.sql"), "r") as file:
#                         og_query = file.read()

# for chain in clickhouse_configs:
#         print(     'clickhouse: ' + chain['blockchain'])
#         query = og_query
#         #Pass in Params to the query
#         query = query.replace("@blockchain@", chain['blockchain'])
#         query = query.replace("@name@", chain['name'])
#         query = query.replace("@layer@", chain['layer'])
#         query = query.replace("@trailing_days@", str(chain['trailing_days']))
        
#         df = ch_client.query_df(query)

#         ch_dfs.append(df)

# ch = pd.concat(ch_dfs)
# ch['source'] = 'goldsky'
# ch['dt'] = pd.to_datetime(ch['dt']).dt.tz_localize(None)
# ch = ch[['dt','blockchain','name','layer','num_qualified_txs','source']]


# In[ ]:


# Step 1: Filter dune_df for chains not in flip
# filtered_dune_df = dune_df[~dune_df['blockchain'].isin(flip['blockchain'])]
# Step 2: Union flip and filtered_dune_df
# combined_flip_dune = pd.concat([flip, filtered_dune_df])
# # Step 3: Filter ch for chains not in combined_flip_dune
# filtered_ch = ch[~ch['blockchain'].isin(combined_flip_dune['blockchain'])]
# # Step 4: Union the result with filtered_ch
# final_df = pd.concat([combined_flip_dune, filtered_ch])
# # final_df
unified_deployers_df = dune_df


# In[ ]:


opstack_metadata = pd.read_csv('../op_chains_tracking/outputs/chain_metadata.csv')
# Filter for rows where is_op_chain is True and dune_schema_name is not null
op_chains_df = opstack_metadata[(opstack_metadata['is_op_chain']) & (opstack_metadata['dune_schema'].notnull())]
# Get the unique entries in dune_schema_name
op_chains = op_chains_df['dune_schema'].unique().tolist()

op_chains
# op_chains = opstac


# In[ ]:


# Ensure created_dt is in datetime format
unified_deployers_df['created_dt'] = pd.to_datetime(unified_deployers_df['created_dt'])

# Generate a date range for the period you want to analyze
start_date = unified_deployers_df['created_dt'].min()
end_date = unified_deployers_df['created_dt'].max()

date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Initialize a list to store results
results = []

# Iterate over each date in the range
for single_date in date_range:
    # Define the date window
    window_start = single_date - timedelta(days=28)
    window_end = single_date
    
    # Filter the dataframe for the current window
    window_df = unified_deployers_df[
        (unified_deployers_df['created_dt'] >= window_start) &
        (unified_deployers_df['created_dt'] <= window_end)
    ]
    
    # Group by blockchain and count unique creator_addresses
    unique_counts = window_df.groupby(['blockchain','name','layer'])['creator_address'].nunique().reset_index()
    unique_counts['date'] = single_date
    # Append the individual blockchain results
    results.append(unique_counts)

    # Calculate the 'All' unique count
    all_count = window_df['creator_address'].nunique()
    results.append(pd.DataFrame({
        'blockchain': ['all'],
        'name': ['All'],
        'layer': ['Aggregate'],
        'creator_address': [all_count],
        'date': [single_date]
    }))
    # Calculate the 'OP Chains' unique count
    layers = ['L1','L2','L3']
    for i in layers:
        l_window_df = window_df[window_df['layer'] == i]
        l_count = l_window_df['creator_address'].nunique()
        results.append(pd.DataFrame({
            'blockchain': [i.lower()],
            'name': [i + 's'],
            'layer': ['Aggregate'],
            'creator_address': [l_count],
            'date': [single_date]
        }))
    # Calculate the 'OP Chains' unique count
    op_window_df = window_df[window_df['blockchain'].isin(op_chains)]
    op_count = op_window_df['creator_address'].nunique()
    results.append(pd.DataFrame({
        'blockchain': ['op chains'],
        'name': ['OP Chains'],
        'layer': ['Aggregate'],
        'creator_address': [op_count],
        'date': [single_date]
    }))

# Concatenate all results into a single DataFrame
final_df = pd.concat(results)

# Optional: Reset index for better readability
final_df = final_df.reset_index(drop=True)

# print(final_df)


# In[ ]:


final_df.sample(5)


# In[ ]:


opstack_metadata['display_name_lower'] = opstack_metadata['display_name'].str.lower()
final_df['display_name_lower'] = final_df['name'].str.lower()

meta_cols = ['is_op_chain','mainnet_chain_id','op_based_version', 'alignment','chain_name', 'display_name','display_name_lower']

final_enriched_df = final_df.merge(opstack_metadata[meta_cols], on='display_name_lower', how = 'left')
final_enriched_df['alignment'] = final_enriched_df['alignment'].fillna('Other EVMs')
final_enriched_df['is_op_chain'] = final_enriched_df['is_op_chain'].fillna(False)
final_enriched_df['display_name'] = final_enriched_df['display_name'].fillna(final_enriched_df['name'])

final_enriched_df = final_enriched_df.drop(columns=['name'])


# In[ ]:


final_enriched_df.sort_values(by=['date','blockchain'], ascending =[False, False], inplace = True)

final_enriched_df.to_csv('outputs/filter_deployer_counts.csv', index=False)

