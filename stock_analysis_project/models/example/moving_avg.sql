SELECT 
  symbol,
  date,
  close,
  AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
FROM USER_DB_BEETLE.raw.stock_data

