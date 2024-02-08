from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import pandas as pd, google.generativeai as palm
import time



def third_stage(data_path, job, palm_api_list):

    def generate_probability(row, job, API_list):
        prompt_test = f"reply with just the probability (with 2 decimal places) that this description '{row['description']}' with this role '{row['role']}' with this title '{row['title']}'is suitable for this job '{job}'"

        for api_index in range(len(API_list)):
            try:
                palm.configure(api_key=API_list[api_index])
                completion = palm.generate_text(prompt=prompt_test, model="models/text-bison-001", temperature=0.2)
                if completion.result is None:
                    return 0
                else:
                    return 100 * float(completion.result)
            except Exception :
                time.sleep(1)

        return 0

    def process_row(args):
        row, job, API_list = args
        return generate_probability(row, job, API_list)
    
    with open(palm_api_list, 'r') as file:
        api_list = file.readlines()

    API_list = [api.strip() for api in api_list]
    
    try:
        df = pd.read_excel(data_path, sheet_name="main")
        dates_df = pd.read_excel(data_path, sheet_name="dates")
        backgrounds_df = pd.read_excel(data_path, sheet_name="backgrounds")
        languages_df = pd.read_excel(data_path, sheet_name="languages")

    except FileNotFoundError:
        return
    
    with ThreadPoolExecutor() as executor:
        args_list = [(row, job, API_list) for _, row in df.iterrows()]
        results = list(tqdm(executor.map(process_row, args_list), total=len(df), desc="Processing"))

    df['probability'] = results

    with pd.ExcelWriter(data_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='main', index=False)
        dates_df.to_excel(writer, sheet_name='dates', index=False)
        backgrounds_df.to_excel(writer, sheet_name='backgrounds', index=False)
        languages_df.to_excel(writer, sheet_name='languages', index=False)
