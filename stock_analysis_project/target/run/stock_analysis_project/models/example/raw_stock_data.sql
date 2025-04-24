
  create or replace   view USER_DB_BEETLE.analytics.raw_stock_data
  
   as (
    -- models/raw_stock_data.sql
select * from raw.stock_data
  );

