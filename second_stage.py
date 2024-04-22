from ftfy import fix_text
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
import re, requests , json , pandas as pd
from opencage.geocoder import OpenCageGeocode, RateLimitExceededError
import time


def second_stage(urls_path, data_path):

    def convert_to_usd(salary, currency, exchange_rates):
        if currency == 'USD':
            return salary
        elif salary is None:
            return 0
        else:
            return salary / exchange_rates[currency]
        
    def categorize_period(period):
        if pd.isna(period):
            return ''
        elif pd.Timedelta('6 days') <= period <= pd.Timedelta('84 days'):  # 12 weeks converted to days
            return 'Short'
        elif pd.Timedelta('90 days') <= period < pd.Timedelta('200 days'):  # 3-6 months converted to days
            return 'Medium'
        else:
            return 'Long'

    def process_url(url):

        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text
            json_data = re.findall(r'type\s*=\s*"application/json">\s*({.*?})\s*</script>', html_content, re.DOTALL)
            json_string = json_data[0]
            return json_string
        else:
            print(f'Error: Unable to retrieve HTML content for URL {url}. Status code {response.status_code}')
            return None    

    def create_record(df, json_data, dates_df, backgrounds_df, languages_df):

        data = json.loads(json_data)
        
        row = {
            'role': data['props']['pageProps']['role']['roleInfo']['learning_points'],
            'opportunity_id': data['query']['opportunityId'],
            'is_premium': data['props']['pageProps']['isPremium'],
            'opportunity_type': data['props']['pageProps']['opportunityType'],
            'product': data['props']['pageProps']['product'],
            'is_favorite': data['props']['pageProps']['isFavorite'],
            'title': data['props']['pageProps']['detailsSummary']['title'],
            'company_name': data['props']['pageProps']['detailsSummary']['companyName'],
            'location': data['props']['pageProps']['detailsSummary']['location'],
            'salary': data['props']['pageProps']['detailsSummary']['specificsInfo']['salary'],
            'salary_periodicity': data['props']['pageProps']['detailsSummary']['specificsInfo']['salary_periodicity'],
            'alphabetic_code': data['props']['pageProps']['detailsSummary']['specificsInfo']['salary_currency']['alphabetic_code'],
            'description': data['props']['pageProps']['role']['description'],
            'accommodation_covered': data['props']['pageProps']['logisticsInfo']['accommodation_covered'],
            'accommodation_provided': data['props']['pageProps']['logisticsInfo']['accommodation_provided'],
            'computer_provided': data['props']['pageProps']['logisticsInfo']['computer_provided'],
            'food_covered': data['props']['pageProps']['logisticsInfo']['food_covered'],
            'food_provided': data['props']['pageProps']['logisticsInfo']['food_provided'],
            'no_of_meals': data['props']['pageProps']['logisticsInfo']['no_of_meals'],
            'transportation_covered': data['props']['pageProps']['logisticsInfo']['transportation_covered'],
            'transportation_provided': data['props']['pageProps']['logisticsInfo']['transportation_provided'],
            'study_levels': ', '.join(level["name"] for level in data['props']['pageProps']['eligibilityData']['studyLevels']),
        
        }

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        
        for slot in data["props"]["pageProps"]["availableSlots"]["availableSlots"]:
            dates_row = {
                'opportunity_id': data['query']['opportunityId'],
                'start_date': slot["start_date"],
                'applications_close_date': slot["applications_close_date"],
                'end_date': slot["end_date"],
                'available_openings': slot["available_openings"],
                'status': slot["status"],
            }
            dates_df = pd.concat([dates_df, pd.DataFrame([dates_row])], ignore_index=True)  
         
        for slot in data["props"]["pageProps"]["detailsSummary"]["backgrounds"]:
            background_row = {
                'opportunity_id': data['query']['opportunityId'],
                'background': slot["constant_name"],
            }
            backgrounds_df = pd.concat([backgrounds_df, pd.DataFrame([background_row])], ignore_index=True)

        for language in data["props"]["pageProps"]["detailsSummary"]["languages"]:
            language_row = {
                'opportunity_id': data['query']['opportunityId'],
                'language': language["constant_name"],
                'language_option': language["option"],
            }
            languages_df = pd.concat([languages_df, pd.DataFrame([language_row])], ignore_index=True)

        return df, dates_df, backgrounds_df, languages_df

    def remove_non_utf8(text):
        if isinstance(text, str):
            return fix_text(text)
        else:
            return text

    def get_lat_long_country(row):
        location = row.location
        if location is None:
            return None, None, None, None
        else:
            while True:
                try:
                    results = geocoder.geocode(location) 
                    if results and len(results):
                        latitude = results[0]['geometry']['lat']
                        longitude = results[0]['geometry']['lng']
                        components = results[0]['components']
                        country = components.get('country', None)
                        continent = components.get('continent', None) 
                        return latitude, longitude, country, continent
                    else:
                        return None, None, None, None

                except RateLimitExceededError:
                    print("geocoder rate exceeded .. ")
                    time.sleep(1)

    try:
        urls_df = pd.read_csv(urls_path)
    except FileNotFoundError:
        return

    not_processed_df = urls_df[urls_df['status'] == 'not_processed']

    if not_processed_df.empty:
        return

    
    df = pd.DataFrame()
    dates_df = pd.DataFrame()
    backgrounds_df = pd.DataFrame()
    languages_df = pd.DataFrame()

    with ThreadPool() as pool:
        results = list(tqdm(pool.imap(process_url, not_processed_df['urls']), total=len(not_processed_df), desc="Processing URLs"))

    for json_string in results:
        df, dates_df, backgrounds_df, languages_df= create_record(df, json_string, dates_df, backgrounds_df, languages_df)
    
    df = df.apply(lambda col: col.apply(remove_non_utf8))
    
    geocoder = OpenCageGeocode('e091c0db134d4597b8bf796cdabaff56')
    
    with ThreadPool() as pool:
        results = list(tqdm(pool.imap(get_lat_long_country, df.itertuples(index=False)), total=len(df), desc="Processing Lat-Long-Country"))

    df[['latitude', 'longitude', 'country','continent']] = pd.DataFrame(results, columns=['latitude', 'longitude', 'country', 'continent'])

    currency_conversions = {}

    for currency, exchange_rate in requests.get('https://open.er-api.com/v6/latest/USD').json()['rates'].items():
        currency_conversions[currency] = exchange_rate
    
    
    df['salary'].fillna(0, inplace=True)
    df['salary_usd'] = df.apply(lambda row: convert_to_usd(row['salary'], row['alphabetic_code'], currency_conversions) / 12 if row['salary_periodicity'] == 'per year' else convert_to_usd(row['salary'], row['alphabetic_code'], currency_conversions), axis=1)
    df['paid'] = df['salary'] > 0

    
    desired_order = ["opportunity_id", "title","latitude", "longitude", "country","continent","salary_usd", "paid", "accommodation_covered","transportation_covered", "no_of_meals", "opportunity_type", "description","role", "company_name", "is_premium", "is_favorite", "accommodation_provided", "computer_provided","food_covered", "food_provided", "transportation_provided","study_levels"]
    
    df = df[desired_order]

    dates_df['start_date'] = pd.to_datetime(dates_df['start_date'])
    dates_df['end_date'] = pd.to_datetime(dates_df['end_date'])
    dates_df['period'] = dates_df['end_date'] - dates_df['start_date']
    dates_df['period_category'] = dates_df['period'].apply(categorize_period)
    dates_df.drop(['period'], axis=1, inplace=True)

    languages_df['language_option'].fillna("preferred", inplace=True)
    
    with pd.ExcelWriter(data_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='main', index=False)
        dates_df.to_excel(writer, sheet_name='dates', index=False)
        backgrounds_df.to_excel(writer, sheet_name='backgrounds', index=False)
        languages_df.to_excel(writer, sheet_name='languages', index=False)
    

    urls_df.loc[urls_df['status'] == 'not_processed', 'status'] = 'processed'
    urls_df.to_csv(urls_path, index=False)
    print("Stage 2 - Completed")