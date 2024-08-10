from datetime import datetime
from glob_functions import send_message
import pandas as pd

def third_stage(data_path):
    df = pd.read_excel(data_path, sheet_name="main")
    dates_df = pd.read_excel(data_path, sheet_name="dates")
    if not df.empty:
        filtered_df = df[(df['suitability'] == 1) & (df['salary_usd'] >= 999) ]    
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
            start_dates = dates_df.loc[dates_df['opportunity_id'] == opportunity_id, 'start_date'].tolist()
            unique_start_dates = sorted(set(start_dates))
            start_dates_str = "\n".join(date.strftime('%Y-%m-%d') for date in unique_start_dates)
            periods = [(date.date() - current_date).days for date in unique_start_dates]
            period_categories = dates_df.loc[dates_df['opportunity_id'] == opportunity_id, 'period_category'].tolist()
            message_lines = [f"{title}\n\nID: {opportunity_id}\nSalary in $: {salary}\nCountry: {country}\nOpportunity type: {opportunity_type}\n"]
            for start_date, period, category in zip(start_dates_str.split('\n'), periods, period_categories):
                message_lines.append(f"Start: {start_date} -- Period to start: {period} days. \n -- {category}")
            message_lines.append(f"\nRole:\n{role}")
            send_message('\n'.join(message_lines))


    

    
