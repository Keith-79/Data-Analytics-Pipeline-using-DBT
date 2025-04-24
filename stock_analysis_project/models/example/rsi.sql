WITH gains_losses AS (
  SELECT
    symbol,
    date,
    close,
    close - LAG(close) OVER (PARTITION BY symbol ORDER BY date) AS change
  FROM USER_DB_BEETLE.raw.stock_data
),
rsi_calc AS (
  SELECT *,
    CASE WHEN change > 0 THEN change ELSE 0 END AS gain,
    CASE WHEN change < 0 THEN -change ELSE 0 END AS loss
  FROM gains_losses
)
SELECT
  symbol,
  date,
  AVG(gain) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_gain,
  AVG(loss) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_loss,
  100 - (
    100 / (
      1 + (
        AVG(gain) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
        /
        NULLIF(AVG(loss) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)
      )
    )
  ) AS rsi
FROM rsi_calc
