import mysql.connector
import pandas as pd
from glob_functions import send_message


db_config = {
    'host': 'mysql-63c7a58-jraididhiaeddine-6de9.a.aivencloud.com',
    'port': 20743,
    'user': 'avnadmin',
    'password': 'AVNS_2KsvbgR146fFQOsDE8m',
    'database': 'aiesec_opportunities',
    'ssl_ca': 'files/ca.pem',
    'use_pure': True
}


def create_table_dates():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS dates (
        opportunity_id INT,
        start_date DATE,
        applications_close_date DATE,
        end_date DATE,
        available_openings INT,
        status VARCHAR(255),
        period_category VARCHAR(255),
        PRIMARY KEY (opportunity_id, start_date, end_date)
    );
    """
    cursor.execute(create_table_query)

    connection.commit()
    connection.close()

def create_table_main():

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS main (
        opportunity_id INT PRIMARY KEY,
        title VARCHAR(255),
        latitude FLOAT,
        longitude FLOAT,
        country VARCHAR(255),
        continent VARCHAR(255),
        salary_usd FLOAT,
        paid BOOLEAN,
        accommodation_covered VARCHAR(255),
        transportation_covered VARCHAR(255),
        no_of_meals INT,
        opportunity_type VARCHAR(255),
        description VARCHAR(255),
        role VARCHAR(255),
        company_name VARCHAR(255),
        is_premium BOOLEAN,
        is_favorite BOOLEAN,
        accommodation_provided VARCHAR(255),
        computer_provided VARCHAR(255),
        food_covered VARCHAR(255),
        food_provided VARCHAR(255),
        transportation_provided VARCHAR(255),
        study_levels VARCHAR(255),
        suitability BOOLEAN,
        status VARCHAR(10)
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    connection.close()

def create_table_languages():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS languages (
        opportunity_id INT,
        language VARCHAR(255),
        language_option VARCHAR(255),
        PRIMARY KEY (opportunity_id, language)
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    connection.close()

def create_table_backgrounds():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS backgrounds (
        opportunity_id INT,
        background VARCHAR(255),
        PRIMARY KEY (opportunity_id, background)
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    connection.close()

def is_table_exists(table_name):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    table_exists_query = f"SHOW TABLES LIKE '{table_name}';"
    cursor.execute(table_exists_query)
    result = cursor.fetchone()
    connection.close()
    return result is not None

def extract_old_opportunitunies():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    select_query = f"SELECT opportunity_id FROM main"
    cursor.execute(select_query)
    result_last_n_days = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(result_last_n_days, columns=columns)
    cursor.close()
    connection.close()
    return df

def insert_data_tosql(data_path):
    max_length = 254
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    df = pd.read_excel(data_path, sheet_name="main")
    dates_df = pd.read_excel(data_path, sheet_name="dates")
    backgrounds_df = pd.read_excel(data_path, sheet_name="backgrounds")
    languages_df = pd.read_excel(data_path, sheet_name="languages")


    dates_df['start_date'] = pd.to_datetime(dates_df['start_date'])
    dates_df['end_date'] = pd.to_datetime(dates_df['end_date'])
    dates_df['applications_close_date'] = pd.to_datetime(dates_df['applications_close_date'])

    dates_df = dates_df.groupby(['opportunity_id', 'start_date', 'end_date'], as_index=False).agg({
        'applications_close_date': 'first',
        'available_openings': 'sum',
        'period_category': 'first'
    })

    dates_df['applications_close_date'] = dates_df['applications_close_date'].dt.date
    dates_df['start_date'] = dates_df['start_date'].dt.date
    dates_df['end_date'] = dates_df['end_date'].dt.date

    table_name = "dates"
    if not is_table_exists(table_name):
        create_table_dates()

    for index, row in dates_df.iterrows():
        insert_query = f"""
        INSERT INTO dates (
            opportunity_id, start_date, applications_close_date, end_date, available_openings, period_category
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        );
        """
        values = (
            row['opportunity_id'], row['start_date'], row['applications_close_date'], row['end_date'],
            row['available_openings'], row['period_category']
        )
        try:  
            cursor.execute(insert_query, values)
        except mysql.connector.errors.IntegrityError:
            pass

    if not df.empty:

        df['description'] = df['description'].fillna('')
        df['role'] = df['role'].fillna('')
        
        if any(df['description'].str.len() > max_length) or any(df['role'].str.len() > max_length):
            df['description'] = df['description'].str.slice(0, max_length)
            df['role'] = df['role'].str.slice(0, max_length)

        table_name = "main"
        
        if not is_table_exists(table_name):
            create_table_main()
        

        for index, row in df.iterrows():
            insert_query = f"""
            INSERT INTO main (
                opportunity_id, title, latitude,longitude,country,continent, salary_usd, paid, accommodation_covered,
                transportation_covered, no_of_meals, opportunity_type, description, role,
                company_name, is_premium, is_favorite, accommodation_provided, computer_provided,
                food_covered, food_provided, transportation_provided, study_levels, suitability, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """
            values = (
                row['opportunity_id'], row['title'], row['latitude'], row['longitude'],
                row['country'],row['continent'],row['salary_usd'], row['paid'],
                row['accommodation_covered'],row['transportation_covered'], row['no_of_meals'], row['opportunity_type'],
                row['description'], row['role'], row['company_name'], row['is_premium'],
                row['is_favorite'], row['accommodation_provided'], row['computer_provided'],
                row['food_covered'], row['food_provided'], row['transportation_provided'],
                row['study_levels'], row['suitability'], row['status']
            )

            try:  
                cursor.execute(insert_query, values)
            except mysql.connector.errors.IntegrityError:
                pass


        
        table_name = "backgrounds"
        if not is_table_exists(table_name):
            create_table_backgrounds()
        
        for index, row in backgrounds_df.iterrows():
            insert_query = f"""
            INSERT INTO backgrounds (
                opportunity_id, background
            ) VALUES (
                %s, %s
            );
            """
            values = (
                row['opportunity_id'], row['background']
            )
            try:  
                cursor.execute(insert_query, values)
            except mysql.connector.errors.IntegrityError:
                pass
        
        table_name = "languages"
        if not is_table_exists(table_name):
            create_table_languages()

        for index, row in languages_df.iterrows():
            insert_query = f"""
            INSERT INTO languages (
                opportunity_id, language, language_option
            ) VALUES (
                %s, %s, %s
            );
            """
            values = (
                row['opportunity_id'], row['language'] , row['language_option']
            )
            try:  
                cursor.execute(insert_query, values)
            except mysql.connector.errors.IntegrityError:
                pass
        
        send_message(f"We added {len(df)} opportunities to the database !")
        
    connection.commit()
    connection.close()

def update_status(urls):
    df = pd.read_csv(urls)
    df = df[(df['updating_status'] == 'not_processed') | (df['scraping_status'] == 'not_processed')] 
    opportunity_ids = df['opportunity_id'].astype(str).tolist()
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("UPDATE main SET status = 'expired';")
    ids_str = ', '.join([f"'{id}'" for id in opportunity_ids])
    query = f"""
    UPDATE main
    SET status = 'live'
    WHERE opportunity_id IN ({ids_str});
    """
    cursor.execute(query)
    connection.commit()
    connection.close()


