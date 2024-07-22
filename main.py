#scraper_project V4.01

from first_stage import browsing
from second_stage import second_stage
from third_stage import third_stage
from sql_integration import insert_data_tosql

urls_path = 'files/urls.csv'
data_path = 'files/all_data.xlsx'
opp_id_sent_path = "files/oppid_sent.csv"

key_words_to_find_in_role = ["analyst", "data", "power bi", "dashboard", "analyze", "analyzing", "powerbi", "analytics", "kpi"]

bad_keywords_to_eliminate_in_title = ['social', 'marketing', 'engine', 'engineering', 'engineer', 'russian', 'swedish', 'romanian',
            'french', 'media', 'spanish', 'dannish', 'portuguese', 'web', 'polish', 'norwegian', 'legal',
            'italian', 'digital', 'sales', 'sale', 'customer', 'content', 'technical', 'community', 'accounting']

suitable_languages = {'English', 'Arabic', 'French'}

browsing(urls_path)
second_stage(urls_path, data_path , key_words_to_find_in_role , suitable_languages, bad_keywords_to_eliminate_in_title)
insert_data_tosql(data_path)
third_stage(opp_id_sent_path, data_path)
print("done!")
