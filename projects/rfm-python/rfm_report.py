"""RFM-сегментация клиентов дилера: читает dealer.db и печатает сегменты.
Запуск:  python rfm_report.py dealer.db"""
import sqlite3, sys

SQL = """
WITH agg AS (
  SELECT c.customer_name AS name,
         CAST(julianday('now') - julianday(MAX(t.transaction_date)) AS INTEGER) AS recency,
         COUNT(*) AS frequency, SUM(t.amount) AS monetary
  FROM customers c JOIN transactions t USING (customer_id)
  GROUP BY c.customer_id
),
scored AS (
  SELECT *, NTILE(5) OVER (ORDER BY recency DESC) AS r,
            NTILE(5) OVER (ORDER BY frequency)    AS f,
            NTILE(5) OVER (ORDER BY monetary)     AS m
  FROM agg
)
SELECT name, recency, frequency, monetary, r, f, m,
  CASE WHEN r >= 4 AND f >= 4 THEN 'VIP'
       WHEN r >= 3 AND f >= 3 THEN 'Loyal'
       WHEN r >= 4 AND f <= 2 THEN 'New'
       WHEN r <= 2 AND f >= 4 THEN 'At Risk'
       WHEN r <= 2 AND f <= 2 THEN 'Lost'
       ELSE 'Regular' END AS segment
FROM scored ORDER BY monetary DESC
"""

def main(path="dealer.db"):
    rows = sqlite3.connect(path).execute(SQL).fetchall()
    counts = {}
    for name, rec, freq, mon, r, f, m, seg in rows:
        counts[seg] = counts.get(seg, 0) + 1
        print(f"{seg:8} {name:32} {rec:4} дн  {freq:3} покупок  {mon/1e6:8.1f} млн")
    print("\nСегменты:", counts)

if __name__ == "__main__":
    main(*sys.argv[1:2])
