from flask import Flask, render_template, jsonify
from threading import Thread
from first_stage import browsing
from second_stage import second_stage
from third_stage import third_stage
from sql_integration import insert_data_tosql , update_status
from glob_functions import cleaning


urls_path = 'files/urls.csv'
data_path = 'files/all_data.xlsx'

files = [urls_path, data_path]

key_words_to_find_in_role = ["analyst", "analysis", "data", "power bi", "dashboard", "analyze", "analyzing", "powerbi", "analytics", "kpi"]

bad_keywords_to_eliminate_in_title = ['social', 'marketing', 'engine', 'engineering', 'engineer', 'russian', 'swedish', 'romanian',
            'french', 'media', 'spanish', 'dannish', 'portuguese', 'web', 'polish', 'norwegian', 'legal',
            'italian', 'digital', 'sales', 'sale', 'customer', 'content', 'technical', 'community', 'accounting']

suitable_languages = {'English', 'Arabic', 'French'}

app = Flask(__name__)

def run_scraping_tasks():
    browsing(urls_path)
    second_stage(urls_path, data_path, key_words_to_find_in_role, suitable_languages, bad_keywords_to_eliminate_in_title)
    insert_data_tosql(data_path)
    update_status(urls_path)
    third_stage(data_path)
    cleaning(files)
    print('done')


@app.route('/scraping', methods=['GET'])
def scrape():
    Thread(target=run_scraping_tasks).start()
    return jsonify({"message": "scraping begin"})



@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
