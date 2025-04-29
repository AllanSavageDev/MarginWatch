from bs4 import BeautifulSoup
import pandas as pd
import pymysql
import configparser
import argparse
import os

def extract_table(file_path, div_id):
    # Load the HTML content
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find the <div> with the id "cme"
    # target_div = soup.find('div', id='cme')
    target_div = soup.find('div', id=div_id)

    # Check if the <div> with id "cme" is found and contains a table
    if target_div:
        # Find the first table inside the <div>
        cme_table = target_div.find('table')

        # Ensure the table exists
        if cme_table:
            # Extract table headers
            headers = [th.get_text(strip=True) for th in cme_table.find_all('th')]

            # Print headers to verify
            # print("Headers found!!:", headers)

            # Extract table rows
            rows = []
            for row in cme_table.find_all('tr'):
                cols = [col.get_text(strip=True) for col in row.find_all('td')]
                if len(cols) > 0:  # Ignore empty rows
                    rows.append(cols)

            # # Print each row to verify
            # for idx, row in enumerate(rows):
            #     print(f"Row {idx + 1}: {row}")

            # Convert to pandas DataFrame
            df = pd.DataFrame(rows, columns=headers)

            df.columns = df.columns.str.lower().str.replace(' ', '_')

            # Rename 'exchange_cme' to 'exchange'
            df.rename(columns={f"exchange_{div_id.lower()}": 'exchange'}, inplace=True)

            # # Print entire DataFrame to verify all data is captured
            # print("\nDataFrame:\n", df)

            return df
        else:
            print(f"\n\nNo table found inside the '{div_id}' div.\n\n")
            return None
    else:
        print(f"\n\nDiv with id '{div_id}' not found.\n\n")
        return None


def create_table(df, table_name, host, user, password, database):
    # Establish the MySQL connection
    connection = None
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor()

        # Check if the table already exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()

        if result:
            # print(f"\nTable '{table_name}' already exists.\n")
            return
        else:
            print(f"\nTable '{table_name}' does not exist. Creating the table.\n")

        # Start the CREATE TABLE query and add the id column as an auto-increment primary key
        create_table_query = f"""
            CREATE TABLE {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                inserted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        """

        # Iterate over the columns of the DataFrame by checking the actual values
        for column in df.columns:
            all_numeric = True  # Assume all values are numeric initially

            # Check each value in the column to see if it's numeric
            for value in df[column]:
                try:
                    float(value)  # Try converting the value to float
                except ValueError:
                    all_numeric = False  # If conversion fails, it's not numeric
                    break  # No need to check further if a non-numeric value is found

            # If all values were numeric, set the column as DOUBLE
            if all_numeric:
                create_table_query += f"`{column}` DOUBLE, "
            else:
                create_table_query += f"`{column}` VARCHAR(255), "

        # Remove the trailing comma and space, and close the query with a parenthesis
        create_table_query = create_table_query.rstrip(", ") + ");"

        # # Print the generated SQL query
        # print(create_table_query)

        # Execute the table creation query
        cursor.execute(create_table_query)
        connection.commit()

        print(f"\nTable '{table_name}' created successfully.\n")

    except pymysql.MySQLError as e:
        print(f"Error occurred while creating the table: {e}")
    finally:
        # Close the cursor and connection
        if connection:
            cursor.close()
            connection.close()


def insert_dataframe_to_mysql(df, table_name, host, user, password, database):
    # Establish the MySQL connection
    connection = None
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (
            exchange, underlying, product_description, trading_class, 
            intraday_initial1, intraday_maintenance1, overnight_initial, 
            overnight_maintenance, currency, has_options, 
            short_overnight_initial, short_overnight_maintenance
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Iterate through each row in the DataFrame
        for _, row in df.iterrows():
            # Extract values from each row
            values = (
                row['exchange'], row['underlying'], row['product_description'],
                row['trading_class'], row['intraday_initial1'], row['intraday_maintenance1'],
                row['overnight_initial'], row['overnight_maintenance'], row['currency'],
                row['has_options'], row['short_overnight_initial'], row['short_overnight_maintenance']
            )

            # Execute the SQL query with the row values
            cursor.execute(insert_query, values)

        # Commit the transaction
        connection.commit()

        # Close the cursor
        cursor.close()

        print(f"Data inserted successfully into {table_name}.")

    except pymysql.MySQLError as e:
        print(f"Error occurred while inserting data into MySQL: {e}")
    finally:
        # Close the cursor and connection
        if connection:
            connection.close()


def process_import(file_path, div_id, table_name, host, user, password, database):

    # Call the function to extract CME table
    df = extract_table(file_path, div_id)

    if df is not None:
        # You can now use the DataFrame (df) for further processing or database insertion
        print("Table successfully extracted and converted to DataFrame.")
        create_table(df, table_name, host, user, password, database)
        insert_dataframe_to_mysql(df, table_name, host, user, password, database)
    else:
        print("Table extraction failed.")


def main():
    # Get the directory where the current script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the full path to the config file
    config_path = os.path.join(script_dir, 'config.ini')

    config = configparser.ConfigParser()
    config.read(config_path)




    # # Load configuration from the config.ini file
    # config = configparser.ConfigParser()
    # config.read('config.ini')

    # 2024-09-29-09-08-12-margin_futures_fops.html

    # Parse command-line arguments to get the filename
    parser = argparse.ArgumentParser(description='Process the filename')
    parser.add_argument('filename', type=str, help='The name of the file to process')
    args = parser.parse_args()

    # Path to your HTML file
    file_path = config['paths']['base_directory']

    # Get the base directory from the config file
    base_directory = config['paths']['base_directory']

    # Construct the full file path
    file_path = os.path.join(base_directory, args.filename)

    # MySQL connection details
    host = config['mysql']['host']
    user = config['mysql']['user']
    password = config['mysql']['password']
    database = config['mysql']['database']
    table_name = config['mysql']['table_name']

    process_import(file_path, "cme", "ib_margins", host, user, password, database)
    process_import(file_path, "cbot", "ib_margins", host, user, password, database)
    process_import(file_path, "cfe", "ib_margins", host, user, password, database)
    process_import(file_path, "COMEX", "ib_margins", host, user, password, database)
    process_import(file_path, "EUREX", "ib_margins", host, user, password, database)
    process_import(file_path, "iceus", "ib_margins", host, user, password, database)
    process_import(file_path, "nybot", "ib_margins", host, user, password, database)
    process_import(file_path, "nymex", "ib_margins", host, user, password, database)
    process_import(file_path, "nyseliffe", "ib_margins", host, user, password, database)

if __name__ == '__main__':
    main()