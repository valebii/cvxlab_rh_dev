#%%
def pass_model_settings(to_H, model_folder_path, start=False):
    import os
    import shutil
    if start:
        src = os.path.join(model_folder_path, 'defaults', 'model_settings_start.xlsx')
    else:
        src = os.path.join(model_folder_path, 'defaults', 'model_settings_default.xlsx')
    
    dst_folder = os.path.join(model_folder_path, f'H{to_H}')
    dst = os.path.join(dst_folder, 'model_settings.xlsx')
    os.makedirs(dst_folder, exist_ok=True)
    print(f"Copying model_settings.xlsx to horizon H{to_H}")
    shutil.copyfile(src, dst)

# %%

def get_planned_cap(model, delta, fh_len, years):
    df = model.variable(name='Cap_plan').reset_index().rename(columns={'index': 'year'})
    df = df.melt(id_vars=['year'], value_name='cap_plan_ex')
    upper_bound = min(years) + delta + fh_len 
    df = df.loc[df['year']< upper_bound]
    df.rename(columns={'year': 'years_Name','variable':'techs_Name', 'cap_plan_ex': 'values'}, inplace=True)
    return df


def update_sets(to_H, years, model_folder_path, delta, start=False):
    import pandas as pd
    import os
    print(f"Updating sets.xlsx to horizon H{to_H}")

    default_sets_path = os.path.join(model_folder_path, 'defaults', 'sets.xlsx')
    output_sets_path = os.path.join(model_folder_path, f'H{to_H}', 'sets.xlsx')
    sets_default  = pd.read_excel(default_sets_path, sheet_name='_set_YEARS')
    sets = sets_default.copy()
    sets['years_scope'] = sets['years_scope'].astype('object')

    if start:
            sets['years_scope'] = 'model'
    else:
        sets.loc[sets['years_Name'] < min(years), 'years_scope'] = 'historical'
        lower_bound = min(years)
        upper_bound = lower_bound + delta
        sets.loc[(sets['years_Name'] >= lower_bound) & (sets['years_Name'] <= upper_bound), 'years_scope'] = 'overlap'
        sets.loc[(sets['years_Name'] >= upper_bound), 'years_scope'] = 'model'
    
    os.makedirs(os.path.join(model_folder_path, f'H{to_H}'), exist_ok=True)
    with pd.ExcelWriter(output_sets_path, engine='openpyxl') as writer:
        # Read all sheets from the default file
        all_sheets = pd.read_excel(default_sets_path, sheet_name=None)
        for sheet_name, df in all_sheets.items():
            if sheet_name == '_set_YEARS':
                sets.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

#%%

def update_input_data(to_H, years, model_folder_path, delta, fh_len, model = None, start=False):
    import pandas as pd
    import os
    default_inputs = os.path.join(model_folder_path, 'defaults', 'input_data_default')
    output_path = os.path.join(model_folder_path, f'H{to_H}', 'input_data')
    demand_path = os.path.join(model_folder_path, 'defaults', 'demand.xlsx')
    demand = pd.read_excel(demand_path, sheet_name='raw')
    demand_update = demand[f'H{to_H}']
    upper_bound = min(years) + delta
    os.makedirs(output_path, exist_ok=True)

    for filename in os.listdir(default_inputs):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(default_inputs, filename)
            try:
                df = pd.read_excel(file_path)
                print(f"Processing {filename}...")
                sheet_name = filename.replace('.xlsx', '')

                if sheet_name == 'Y':
                    df.loc[df['flows_agg_Name']=='Energia elettrica', 'values'] = demand_update.values
 
                if filename == 'cap_plan_ex.xlsx':
                    df.loc[df['years_Name']>=upper_bound,'values'] = 0
                    if start:
                        df.loc[df['years_Name']<=upper_bound,'values'] = 0
                    else:
                        vals = get_planned_cap(model, delta, fh_len, years)
                        df.update(vals)

    
                df.to_excel(os.path.join(output_path, filename), index=False, sheet_name=sheet_name)
                    # Reset the index and set it as a column named 'id' starting from 1
            except Exception as e:
                print(f"Could not read {filename}: {e}")




# # %%
# pass_model_settings(4, model_folder_path)
# update_sets(4, H_group[4], model_folder_path)
# update_input_data(4, H_group[4], model_folder_path)
# # %%
#%%

# import pandas as pd
# model_folder_path = 'C:/Users/baioc/OneDrive - Politecnico di Milano/PhD/CVXLAB/Concepts/Rolling/'
# Y = pd.read_excel(model_folder_path + 'defaults/input_data_default/Y.xlsx')
# # %%
# demand_path = os.path.join(model_folder_path, 'defaults', 'demand.xlsx')
# demand = pd.read_excel(demand_path, sheet_name='raw')
# demand = demand.loc[demand['year'].isin(range(2000,2026))]
# demand_update = demand[f'H{1}']

# # %%
# Y.loc[Y['flows_agg_Name']=='Energia elettrica', 'values'] = demand_update.values

# # %%
