#scraper_project V3

from first_stage import browsing
from second_stage import second_stage
from third_stage import third_stage
from sql_integration import insert_data_tosql

urls_path = 'urls.csv'
data_path = 'all_data.xlsx'
palm_api_list = 'Palm_api_list.txt'
job = "data analyst"
preferences = "not good in marketing xD"


browsing(urls_path)
second_stage(urls_path, data_path)
third_stage(data_path, job, palm_api_list)
insert_data_tosql(data_path)
print("done!")
