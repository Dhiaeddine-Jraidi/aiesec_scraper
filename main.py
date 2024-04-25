#scraper_project V3.1

from first_stage import browsing
from second_stage import second_stage
from third_stage import third_stage
from sql_integration import insert_data_tosql

urls_path = 'files/urls.csv'
data_path = 'files/all_data.xlsx'
palm_api_list = 'files/Palm_api_list.txt'
opp_id_sent_path = "files/oppid_sent.csv"



job = "data analyst"
preferences = "not good in marketing xD"
suitable_languages = {'English', 'Arabic', 'French'}



browsing(urls_path)
second_stage(urls_path, data_path, suitable_languages)
third_stage(opp_id_sent_path, data_path, job, palm_api_list)
insert_data_tosql(data_path)
print("done!")
