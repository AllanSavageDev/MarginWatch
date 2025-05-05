import os
import argparse
import configparser
import pandas as pd
import psycopg2
from bs4 import BeautifulSoup

print(">>> main.py starting")



def get_db_connection(config):
    return psycopg2.connect(
        host=config['host'],
        port=int(config['port']),
        user=config['user'],
        password=config['password'],
        dbname=config['database']
    )


def main():
    
    env = os.getenv('MW_ENV', 'dev')  # defaults to 'dev' if not set
    filename = f'config.{env}.ini'

    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, filename)
    config = configparser.ConfigParser()
    config.read(config_path)

    from db import load_db_config  # adjust if it's in the same file

    db_config = load_db_config()

    base_directory = config['paths']['base_directory']

    parser = argparse.ArgumentParser(description='Process the filename')
    parser.add_argument('filename', type=str, nargs='?', help='The name of the file to process')
    
    args = parser.parse_args()

    if args.filename:
        file_path = os.path.join(base_directory, args.filename)
    else:
        # Automatically select the latest file
        files = [f for f in os.listdir(base_directory) if f.endswith(".html")]
        if not files:
            print("No margin files found.")
            return
        latest = max(files, key=lambda f: os.path.getctime(os.path.join(base_directory, f)))
        file_path = os.path.join(base_directory, latest)
        print(f"Auto-selected latest file: {latest}")

    # Proceed with using file_path...

    div_ids = ["BURSAMY","CEDX","cfe","cme","COMEX","ENDEX","EUREX","fta","hkfe","iceeu","iceeusoft","iceus","idem","ipe","kse","lmeotc","matif","meffrv","mexder","monep","nse","nybot","nymex","nyseliffe","oms","osejpn","QBALGOIEU","QBALGOIUS","sgx","snfe"]

    for div_id in div_ids:
        process_import(file_path, div_id, "ib_margins", db_config)



def process_import(file_path, div_id, table_name, config):
    
    df = extract_table(file_path, div_id)
    
    if df is not None:
        print(f"Data extracted for div '{div_id}'.")
        
        create_table(df, table_name, config)
        
        insert_dataframe(df, table_name, config)
    else:
        print(f"No data extracted for div '{div_id}'.")


def extract_table(file_path, div_id):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    target_div = soup.find('div', id=div_id)
    if not target_div:
        print(f"\nDiv with id '{div_id}' not found.\n")
        return None

    cme_table = target_div.find('table')
    if not cme_table:
        print(f"\nNo table found inside the '{div_id}' div.\n")
        return None

    headers = [th.get_text(strip=True) for th in cme_table.find_all('th')]
    rows = [
        [col.get_text(strip=True) for col in row.find_all('td')]
        for row in cme_table.find_all('tr') if row.find_all('td')
    ]

    df = pd.DataFrame(rows, columns=headers)
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df.rename(columns={f"exchange_{div_id.lower()}": 'exchange'}, inplace=True)
    return df


def create_table(df, table_name, config):
    connection = None
    try:
        connection = get_db_connection(config)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = %s
            );
        """, (table_name,))
        if cursor.fetchone()[0]:
            return

        print(f"\nCreating table '{table_name}'.\n")

        create_query = f"""
        CREATE TABLE public."{table_name}" (
            id serial4 NOT NULL,
            inserted_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
            exchange varchar(255) NULL,
            underlying varchar(255) NULL,
            product_description varchar(255) NULL,
            trading_class varchar(255) NULL,
            intraday_initial float8 NULL,
            intraday_maintenance float8 NULL,
            overnight_initial float8 NULL,
            overnight_maintenance float8 NULL,
            currency varchar(255) NULL,
            has_options varchar(255) NULL,
            short_overnight_initial float8 NULL,
            short_overnight_maintenance float8 NULL,
            CONSTRAINT ib_margins_pkey PRIMARY KEY (id)
        );
        """

        cursor.execute(create_query)
        connection.commit()
        print(f"Table '{table_name}' created successfully.")

    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()



def insert_dataframe(df, table_name, config):
    connection = None
    try:
        connection = get_db_connection(config)
        cursor = connection.cursor()

        insert_query = f"""
        INSERT INTO "{table_name}" (
            exchange, underlying, product_description, trading_class,
            intraday_initial, intraday_maintenance, overnight_initial,
            overnight_maintenance, currency, has_options,
            short_overnight_initial, short_overnight_maintenance
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():
            values = (
                row['exchange'], row['underlying'], row['product_description'],
                row['trading_class'], row['intraday_initial1'], row['intraday_maintenance1'],
                row['overnight_initial'], row['overnight_maintenance'], row['currency'],
                row['has_options'], row['short_overnight_initial'], row['short_overnight_maintenance']
            )
            cursor.execute(insert_query, values)

        connection.commit()
        print(f"Inserted data into '{table_name}'.")

    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == '__main__':
    main()
