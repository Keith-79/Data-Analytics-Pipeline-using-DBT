from airflow import DAG
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import yfinance as yf
import pandas as pd
import snowflake.connector
from airflow.models import Variable

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    default_args=default_args,
    description='ETL + dbt ELT pipeline for stock data',
    schedule_interval="@daily",
    catchup=False
)
def full_etl_dbt_pipeline():

    @task
    def fetch_stock_data(symbols):
        """Fetch stock data from Yahoo Finance"""
        data_frames = []
        for symbol in symbols:
            stock = yf.Ticker(symbol)
            df = stock.history(period="180d")
            df['Symbol'] = symbol
            df = df[['Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df.reset_index(inplace=True)
            data_frames.append(df)
        return pd.concat(data_frames)

    @task
    def load_to_snowflake(stock_data_df):
        """Load data into Snowflake"""
        conn = snowflake.connector.connect(
            user=Variable.get("snowflake_username"),
            password=Variable.get("snowflake_password"),
            account=Variable.get("snowflake_account"),
            warehouse="BEETLE_QUERY_WH",
            database="USER_DB_BEETLE"
        )
        cursor = conn.cursor()
        target_table = "USER_DB_BEETLE.raw.stock_data"

        try:
            cursor.execute("BEGIN;")
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {target_table} (
                    symbol VARCHAR,
                    date DATE,
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume BIGINT,
                    PRIMARY KEY (symbol, date));
            """)
            cursor.execute(f"DELETE FROM {target_table}")
            
            for _, row in stock_data_df.iterrows():
                sql = f"""
                    INSERT INTO {target_table} (symbol, date, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    row['Symbol'],
                    row['Date'].strftime('%Y-%m-%d'),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume'])
                ))
            cursor.execute("COMMIT;")
            print(f"Successfully loaded {len(stock_data_df)} rows into {target_table}")
        except Exception as e:
            cursor.execute("ROLLBACK;")
            print(f"Error: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()

    # Task to run dbt models, tests, and snapshots
    run_dbt = BashOperator(
    task_id='run_dbt_transformations',
    bash_command=(
        'export PATH="$PATH:/home/airflow/.local/bin" && '
        'cd "$DBT_PROJECT_DIR" && '
        'dbt run --profiles-dir "$DBT_PROJECT_DIR/config" && '
        'dbt test --profiles-dir "$DBT_PROJECT_DIR/config" && '
        'dbt snapshot --profiles-dir "$DBT_PROJECT_DIR/config"'
    ),
    env={
        'DBT_PROJECT_DIR': '/opt/airflow/dags/stock_analysis_project',
        'DBT_ACCOUNT': 'sfedu02-ksb65579',
        'DBT_DATABASE': 'USER_DB_BEETLE',
        'DBT_PASSWORD': Variable.get("snowflake_password"),
        'DBT_ROLE': 'TRAINING_ROLE',
        'DBT_TYPE': 'snowflake',
        'DBT_USER': Variable.get("snowflake_username"),
        'DBT_WAREHOUSE': 'BEETLE_QUERY_WH'
    }

)

    # DAG flow
    symbols = ["NVDA", "AAPL"]
    stock_data = fetch_stock_data(symbols)
    load_task = load_to_snowflake(stock_data)
    load_task >> run_dbt

# Instantiate the DAG
etl_dbt_dag = full_etl_dbt_pipeline()
