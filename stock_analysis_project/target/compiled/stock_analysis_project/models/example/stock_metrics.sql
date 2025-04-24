-- models/stock_metrics.sql
with raw_data as (
  select *, row_number() over (partition by symbol order by date) as row_num
  from USER_DB_BEETLE.analytics.raw_stock_data
),

calc as (
  select 
    symbol,
    date,
    close,
    avg(close) over (partition by symbol order by date rows between 13 preceding and current row) as ma14,
    avg(close) over (partition by symbol order by date rows between 49 preceding and current row) as ma50
  from raw_data
)

select * from calc