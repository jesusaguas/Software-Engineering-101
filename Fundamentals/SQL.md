# PostgreSQL — Senior Interview Quick Review

This guide builds one query step by step. Assume:

```text
orders(id, user_id, status, total, created_at)
users(id, email, name, created_at)
```

The learning order is intentionally simple. In a finished query, clauses appear
in this order:

```sql
SELECT ...
FROM ...
JOIN ... ON ...
WHERE ...
GROUP BY ...
HAVING ...
ORDER BY ...
LIMIT ...
OFFSET ...;
```

## 1. `SELECT`: choose the result

Start by choosing the columns to return:

```sql
SELECT id, user_id, status, total, created_at
FROM orders;
```

Use aliases for clearer output:

```sql
SELECT
    id AS order_id,
    total AS order_total
FROM orders;
```

Use `DISTINCT` only when duplicate combinations must be removed:

```sql
SELECT DISTINCT status
FROM orders;
```

## 2. `WHERE`: filter rows

Add conditions to the example:

```sql
SELECT id, user_id, status, total, created_at
FROM orders
WHERE status = 'paid'
  AND created_at >= $1
  AND created_at < $2;
```

`$1` and `$2` are PostgreSQL parameters. Parameterized queries prevent SQL
injection and allow plan reuse. You pass them in from your application code, along with the query.

Common conditions:

```sql
WHERE total = 100
WHERE total <> 100
WHERE total > 100
WHERE status IN ('paid', 'shipped')
WHERE total BETWEEN 100 AND 500       -- inclusive
WHERE name LIKE 'Ada%'
WHERE name ILIKE '%ada%'              -- case-insensitive
WHERE cancelled_at IS NOT NULL            -- never: = NULL
WHERE condition AND (other OR another)
```

Useful expressions:

```sql
COALESCE(value, fallback)  -- first non-NULL value
NULLIF(value, 0)           -- NULL when value is 0
CASE WHEN condition THEN result ELSE result END
```

Senior advice:

- `NULL` means unknown; comparisons with it are not `TRUE`.
- Parenthesize mixed `AND` and `OR` conditions.
- Use half-open ranges (`>= start AND < end`) for timestamps.
- Keep indexed columns free of unnecessary functions and casts.

## 3. `ORDER BY`: sort the result

```sql
SELECT id, user_id, status, total, created_at
FROM orders
WHERE status = 'paid'
  AND created_at >= $1
  AND created_at < $2
ORDER BY created_at DESC, id DESC;
```

- `ASC` is the default; `DESC` reverses the order.
- Sort by multiple columns from left to right.
- Add a unique tie-breaker (`id`) for deterministic results.
- PostgreSQL supports `NULLS FIRST` and `NULLS LAST`.

## 4. `LIMIT`: restrict the result size

```sql
SELECT id, user_id, status, total, created_at
FROM orders
WHERE status = 'paid'
  AND created_at >= $1
  AND created_at < $2
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

Always pair `LIMIT` with `ORDER BY` when you need predictable rows.

## 5. `OFFSET`: skip rows

```sql
SELECT id, user_id, status, total, created_at
FROM orders
WHERE status = 'paid'
  AND created_at >= $1
  AND created_at < $2
ORDER BY created_at DESC, id DESC
LIMIT 20
OFFSET 40;
```

`OFFSET 40` skips the first 40 rows. It is simple, but large offsets become
slow and concurrent changes can shift rows between pages.

For large datasets, prefer keyset pagination:

```sql
WHERE status = 'paid'
  AND (created_at, id) < ($1, $2)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

## 6. `GROUP BY`: summarize rows

Change the query's grain from one row per order to one row per user:

```sql
SELECT
    user_id,
    COUNT(*) AS order_count,
    SUM(total) AS total_spent
FROM orders
WHERE status = 'paid'
  AND created_at >= $1
  AND created_at < $2
GROUP BY user_id
ORDER BY total_spent DESC, user_id
LIMIT 20
OFFSET 0;
```

Every selected expression must normally be:

- Included in `GROUP BY`, or
- Calculated with an aggregate function.

### Aggregate functions

```sql
COUNT(*)                 -- all rows
COUNT(column)            -- non-NULL values
COUNT(DISTINCT column)   -- unique non-NULL values
SUM(column)
AVG(column)
MIN(column)
MAX(column)
```

PostgreSQL supports conditional aggregation:

```sql
COUNT(*) FILTER (WHERE status = 'paid')
SUM(total) FILTER (WHERE status = 'paid')
```

Watch for joins that multiply rows before aggregation.

## 7. `HAVING`: filter groups

`HAVING` clause is used to filter groups based on aggregate conditions (SUM(), COUNT(), AVG(), etc.).

`WHERE` filters individual rows before grouping. `HAVING` filters completed
groups after aggregation:

```sql
SELECT
    user_id,
    COUNT(*) AS order_count,
    SUM(total) AS total_spent
FROM orders
WHERE status = 'paid'
  AND created_at >= $1
  AND created_at < $2
GROUP BY user_id
HAVING COUNT(*) >= 3
   AND SUM(total) >= 1000
ORDER BY total_spent DESC, user_id
LIMIT 20
OFFSET 0;
```

Use `WHERE` whenever a condition does not require an aggregate. Filtering
earlier usually reduces the work performed.

## 8. `JOIN`: combine related tables

Add user information to the same report:

```sql
SELECT
    u.id AS user_id,
    u.email,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spent
FROM users AS u
INNER JOIN orders AS o
    ON o.user_id = u.id
WHERE o.status = 'paid'
  AND o.created_at >= $1
  AND o.created_at < $2
GROUP BY u.id, u.email
HAVING COUNT(o.id) >= 3
   AND SUM(o.total) >= 1000
ORDER BY total_spent DESC, u.id
LIMIT 20
OFFSET 0;
```

Core join types:

| Join | Result |
|---|---|
| `INNER JOIN` | Matching rows only |
| `LEFT JOIN`  | Every left row plus matching right rows |
| `RIGHT JOIN` | Every right row plus matching left rows |
| `FULL OUTER JOIN` | Every row from both tables |
| `CROSS JOIN` | Every possible combination |

### `ON` versus `WHERE`

`ON` decides which rows match. `WHERE` filters the joined result.

```sql
-- Keeps every user, including users with no paid orders
SELECT u.name, o.id AS order_id, o.status
FROM users AS u
LEFT JOIN orders AS o
    ON o.user_id = u.id
   AND o.status = 'paid'
```

```
name  | order_id | status
------|----------|-------
Alice | 10       | paid
Bob   | NULL     | NULL
Carol | 13       | paid
```

Here the `AND` condition is part of the join, so users with no paid orders still appear. If you move the condition into `WHERE`, those users are filtered out, effectively turning the `LEFT JOIN` into an `INNER JOIN`:

```sql
-- Filters out users with no paid orders
SELECT u.name, o.id AS order_id, o.status
FROM users AS u
LEFT JOIN orders AS o
    ON o.user_id = u.id
WHERE o.status = 'paid'
```
```
name  | order_id | status
------|----------|-------
Alice | 10       | paid
Carol | 13       | paid
```


Senior advice:

- Join on real relationships, normally primary key to foreign key.
- Understand one-to-one, one-to-many, and many-to-many cardinality.
- Check for accidental row multiplication before aggregating.
- Use `EXISTS` / `NOT EXISTS` when you only need to test whether related rows
  exist.

```sql
-- Give me all users who have never placed an order
SELECT u.*
FROM users AS u
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.user_id = u.id
);
```

Prefer `NOT EXISTS` to `NOT IN (subquery)` when `NULL` may appear.

## 9. Transactions

A transaction makes a multi-statement operation succeed or fail as one unit:

```sql
BEGIN;   -- Start a transaction

SELECT id, status 
FROM orders
WHERE id = $1
FOR UPDATE;   -- Reads and locks the row to prevent concurrent updates

UPDATE orders
SET status = 'cancelled'
WHERE id = $1
  AND status = 'pending'
RETURNING id, status;         -- returns the row only if it was updated (pending -> cancelled)

COMMIT; -- End the transaction, alternatively ROLLBACK to undo changes
```

`FOR UPDATE` locks the selected row until the transaction finishes. PostgreSQL runs all statements atomically by default, so in this case just updating the row is enough to prevent concurrent updates.


See this other transaction:
```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE id = $1
  AND balance >= 100;   -- Bob

UPDATE accounts
SET balance = balance + 100
WHERE id = $2;          -- Alice

COMMIT;
```

PostgreSQL can update both accounts with one statement:
```sql
UPDATE accounts
SET balance = CASE
    WHEN id = $1 THEN balance - 100  -- Bob
    WHEN id = $2 THEN balance + 100  -- Alice
END
WHERE id IN ($1, $2);
```

Know **ACID**:

- **Atomicity**: all changes commit or none do.
- **Consistency**: constraints and invariants remain valid.
- **Isolation**: concurrent transactions do not interfere incorrectly.
- **Durability**: committed changes survive failures.

PostgreSQL levels:

```sql
BEGIN ISOLATION LEVEL READ COMMITTED; -- default
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

Senior advice:

- Keep transactions short.
- Lock rows in a consistent order to reduce deadlocks.
- Check affected-row counts for conditional updates.
- Retry deadlocks and serialization failures with bounded backoff.
- Understand lost updates, non-repeatable reads, write skew, and optimistic
  locking.

## 10. `CREATE TABLE`: define the schema

These tables support the examples above:

```sql
CREATE TABLE users (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- AS IDENTITY means auto-increment
    email      TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    BIGINT NOT NULL
               REFERENCES users(id) ON DELETE RESTRICT, -- RESTRICT means don't delete users with orders
    status     TEXT NOT NULL DEFAULT 'pending'
               CHECK (status IN ('pending', 'paid', 'cancelled')),
    total      NUMERIC(12, 2) NOT NULL CHECK (total >= 0), -- NUMERIC -> max 12 digits, 2 after the decimal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Core constraints:

- `PRIMARY KEY`: unique, non-`NULL` row identity.
- `FOREIGN KEY` / `REFERENCES`: referential integrity.
- `UNIQUE`: prevents duplicate values.
- `NOT NULL`: requires a value.
- `CHECK`: enforces a rule.
- `DEFAULT`: supplies a value when omitted.

Use `NUMERIC`, not floating point, for money. Prefer `TIMESTAMPTZ` for real
points in time. Put critical data integrity rules in the database.

## 11. `CREATE INDEX`: support access patterns

Create indexes for real queries, not every column.

The report repeatedly filters paid orders by date and groups them by user:

```sql
-- Multicolumn/Composite partial index, get the most recent paid orders by user_id, ordered by time
CREATE INDEX idx_orders_paid_created_user
ON orders (user_id, created_at)
INCLUDE (total)
WHERE status = 'paid';
```

This is a **partial** index because it stores only paid orders. `INCLUDE` adds extra columns to the index (**covering** index).


Senior advice:

- B-tree indexes support equality, ranges, sorting, and prefix searches.
- Composite indexes follow the leftmost-prefix rule 
  - (`(a, b)` supports `(a)` but not `(b)`).
- Equality columns commonly precede range and sorting columns 
  - (`(status, created_at)` supports `WHERE status = 'paid' AND created_at >= ...`).
- Indexes consume storage and make writes more expensive.
- Low-selectivity columns rarely make useful standalone indexes.
- Measure the query plan before and after adding an index.
- To index boolean columns, consider a partial index on the `TRUE` or `FALSE` rows.

Keep predicates **sargable** ("Search ARGument ABLE"), meaning allows the database engine to efficiently use an index to find rows, instead of scanning the entire table:

```sql
-- Avoid: function applied to the indexed column
WHERE DATE(created_at) = DATE '2025-01-01'

-- Prefer: searchable range
WHERE created_at >= TIMESTAMPTZ '2025-01-01 00:00:00+00'
  AND created_at <  TIMESTAMPTZ '2025-01-02 00:00:00+00'
```

## 12. `EXPLAIN` and `ANALYZE`: debug performance

Start without executing the query:

```sql
EXPLAIN
SELECT *
FROM orders
WHERE status = 'paid'
  AND created_at >= TIMESTAMPTZ '2025-01-01 00:00:00+00'
  AND created_at <  TIMESTAMPTZ '2025-02-01 00:00:00+00';
```

Then measure real execution:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE status = 'paid'
  AND created_at >= TIMESTAMPTZ '2025-01-01 00:00:00+00'
  AND created_at <  TIMESTAMPTZ '2025-02-01 00:00:00+00';
```

- `EXPLAIN` displays the Execution Plan without running the query.
- `ANALYZE` executes it and shows actual times, rows, and loops.
- `BUFFERS` shows cache and disk-page activity.
- `ANALYZE orders;` refreshes planner statistics.

Look for:

- Large differences between estimated and actual rows.
- Sequential scans on large tables or Index scans on small tables.
- High-cost sorts, repeated loops, or temporary disk usage.
- Whether PostgreSQL chose a nested loop, hash join, or merge join.
- Indexes that are missing—or present but not useful.

Debugging process:

1. Confirm the query is correct and determine its expected row count.
2. Run `EXPLAIN (ANALYZE, BUFFERS)` safely with realistic data.
3. Find the node doing the most work.
4. Reduce rows/columns or fix joins, casts, and predicates.
5. Add or adjust an index only when the access pattern supports it.
6. Run the plan again and compare.

> `EXPLAIN ANALYZE` executes the statement. Be especially careful with
> `UPDATE`, `DELETE`, and other writes.

## Final review

For senior interviews, be ready to explain:

1. The result's grain, ordering, ties, duplicates, and `NULL` behavior.
2. Why each filter belongs in `ON`, `WHERE`, or `HAVING`.
3. How joins affect cardinality before aggregation.
4. Which constraints protect data integrity.
5. Which index matches the query and what it costs on writes.
6. Which transaction and isolation guarantees protect concurrency.
7. What the actual execution plan says—not what you assume it says.
