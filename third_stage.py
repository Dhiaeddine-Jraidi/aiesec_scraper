from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from glob_functions import send_message
import pandas as pd, google.generativeai as palm, time 


def third_stage(opp_id_sent_path, data_path, job, palm_api_list):

    def generate_probability(row, job, API_list):
        prompt_test = f"reply with just the probability (with 2 decimal places) that this role '{row['role']}' with this title '{row['title']}'is suitable for this job '{job}'"
        for api_index in range(len(API_list)):
            try:
                palm.configure(api_key=API_list[api_index])
                completion = palm.generate_text(prompt=prompt_test, model="models/text-bison-001", temperature=0.2)
                if completion.result is None:
                    return 0
                else:
                    return 100 * float(completion.result)
            except Exception :
                time.sleep(0)
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

    try:
        opp_send_df = pd.read_csv(opp_id_sent_path)
    except FileNotFoundError:
        opp_send_df = pd.DataFrame(columns=['opportunity_id'])

    filtered_df = df[(df['probability'] >= 20) & (df['salary_usd'] >= 999) & (~df['opportunity_id'].isin(opp_send_df['opportunity_id']))]    
    current_date = datetime.now().date()
    
    for index, row in filtered_df.iterrows():
        title = row['title']
        opportunity_id = row['opportunity_id']
        salary = int(row['salary_usd'])
        if salary <10:
            salary = "Not Paid"
        role = row['role']
        opportunity_type = row['opportunity_type']
        country = row['country']
        probability = row['probability']
        start_dates = dates_df.loc[dates_df['opportunity_id'] == opportunity_id, 'start_date'].tolist()
        unique_start_dates = sorted(set(start_dates))
        start_dates_str = "\n".join(date.strftime('%Y-%m-%d') for date in unique_start_dates)
        periods = [(current_date - date.date()).days for date in unique_start_dates]
        period_categories = dates_df.loc[dates_df['opportunity_id'] == opportunity_id, 'period_category'].tolist()
        message_lines = [f"{title}\n\nID: {opportunity_id}\nSalary in $: {salary}\nCountry: {country}\nOpportunity type: {opportunity_type}\nProbability: {probability}\n"]
        for start_date, period, category in zip(start_dates_str.split('\n'), periods, period_categories):
            message_lines.append(f"Start: {start_date}. Period to start: {period} days. -- {category}")
        message_lines.append(f"\nRole:\n{role}")
        send_message('\n'.join(message_lines))
        opp_send_df = pd.concat([opp_send_df, filtered_df[['opportunity_id']]], ignore_index=True)    

    opp_send_df.to_csv(opp_id_sent_path, index=False)


    

    
