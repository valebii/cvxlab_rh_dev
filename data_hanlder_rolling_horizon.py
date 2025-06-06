#%%
import pandas as pd
import os

def cut_input_data(years, horizon, model_folder_path):
    print(f"Cutting input data for horizon {horizon} with years {years}")
    defaults_folder_path = model_folder_path + '/defaults/'
    new_path = model_folder_path + f'/H{horizon}/'
    os.makedirs(new_path, exist_ok=True)
    os.makedirs(new_path + 'input_data', exist_ok=True)
    years_name = 'years_Name'
    folder_path = defaults_folder_path + 'input_data_default'
    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(folder_path, filename)
            try:
                df = pd.read_excel(file_path)
                print(f"Processing {filename}...")
                sheet_name = filename.replace('.xlsx', '').replace('.xls', '')

                if years_name in df.columns:
                    # Keep only rows where years_name is in the years range
                    df = df[df[years_name].isin(years)]

                    # if filename == 'Y.xlsx':
                    #     df[df['years_Name'].isin(years)]['values'] = demand_update
                    #     # Save to Excel with sheet name as filename without .xlsx

                df['id'] = range(1, len(df) + 1)
                df.to_excel(os.path.join(new_path, f'input_data/{filename}'), index=False, sheet_name=sheet_name)
                    # Reset the index and set it as a column named 'id' starting from 1
            except Exception as e:
                print(f"Could not read {filename}: {e}")



def cut_sets(years, horizon, model_folder_path):
    print(f"Updating sets.xlsx to horizon H{horizon}")
    default_sets_path = os.path.join(model_folder_path, 'defaults', 'sets.xlsx')
    output_sets_path = os.path.join(model_folder_path, f'H{horizon}', 'sets.xlsx')
    year_sets_default  = pd.read_excel(default_sets_path, sheet_name='_set_YEARS')
    year_sets = year_sets_default.copy()
    year_sets = year_sets[year_sets['years_Name'].isin(years)]
    os.makedirs(os.path.join(model_folder_path, f'H{horizon}'), exist_ok=True)
    with pd.ExcelWriter(output_sets_path, engine='openpyxl') as writer:
        # Read all sheets from the default file
        all_sheets = pd.read_excel(default_sets_path, sheet_name=None)
        for sheet_name, df in all_sheets.items():
            if sheet_name == '_set_YEARS':
                year_sets.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df.to_excel(writer, sheet_name=sheet_name, index=False)


def pass_model_settings(horizon, model_folder_path):
    import os
    import shutil

    src = os.path.join(model_folder_path, 'defaults', 'model_settings_default.xlsx')
    dst_folder = os.path.join(model_folder_path, f'H{horizon}')
    dst = os.path.join(dst_folder, 'model_settings.xlsx')
    os.makedirs(dst_folder, exist_ok=True)
    print(f"Copying model_settings.xlsx to horizon H{horizon}")
    shutil.copyfile(src, dst)

def get_planned_cap(model):
    df = model.variable(name='Cap_plan').reset_index().rename(columns={'index': 'year'})
    df = df.melt(id_vars=['year'], value_name='cap_plan_ex')
    df.rename(columns={'year': 'years_Name','variable':'techs_Name', 'cap_plan_ex': 'values'}, inplace=True)
    df = df[['techs_Name', 'years_Name', 'values']]
    return df

def update_planned_cap(old_horizon, new_horizon, model_folder_path, model, years):
    years_name = 'years_Name'
    print(f"Passing planned cap from {old_horizon} to {new_horizon}")
    defaults_folder_path = model_folder_path + '/defaults/'
    new_path = model_folder_path + f'/H{new_horizon}/'
    os.makedirs(new_path, exist_ok=True)
    os.makedirs(new_path + 'input_data', exist_ok=True)
    file_path = defaults_folder_path + 'input_data_default/cap_plan_ex.xlsx'
    df = pd.read_excel(file_path, index_col=0)
    vals = get_planned_cap(model)
    vals.index.name = 'id'
    vals.index = range(1, len(vals) + 1)
    df=df.fillna(0)
    df.set_index(['techs_Name', 'years_Name'], inplace=True)
    vals.set_index(['techs_Name', 'years_Name'], inplace=True)
    df.update(vals)
    df.reset_index(inplace=True)
    df = df[df[years_name].isin(years)]
    df.to_excel(new_path + 'input_data/cap_plan_ex.xlsx', index=False, sheet_name='cap_plan_ex')
    return vals, df


