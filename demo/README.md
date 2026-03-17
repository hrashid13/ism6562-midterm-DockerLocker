# Grocery Store OLAP - Apache Ignite Distributed Demo

A 3-node Apache Ignite cluster running a distributed star schema built from a grocery store simulation. Demonstrates automatic data partitioning, distributed SQL, and fault tolerance across 3 nodes.

Built for ISM 6562 Big Data for Business @ University of South Florida.

---

## What This Demonstrates

| Concept | How It Shows Up |
|---|---|
| Automatic partitioning | 45k fact rows split across 3 nodes automatically |
| Replicated dimensions | Small dim tables copied to all nodes for fast joins |
| Distributed SQL | Aggregation queries run in parallel across all 3 nodes |
| Fault tolerance | Kill a node mid-demo, queries still return correct results |
| Star schema at scale | Same schema concepts from class, now distributed |

---

## Prerequisites

- Docker Desktop installed and running
- Git

---

## Setup (one time)

```bash
# 1. Clone the repo
git clone https://github.com/hrashid13/apache-ignite-grocery-demo
cd ignite-grocery-demo

# 2. Start the 3-node cluster
docker compose up -d

# 3. Wait about 15 seconds for nodes to discover each other, then load data
docker compose run loader
```

The loader takes about 3 minutes and loads 45k rows of grocery sales data distributed across the 3 nodes. You only need to do this once -- as long as you don't run `docker compose down -v`, the data stays in the volumes.

---

## Running Queries

Open the built-in SQL shell directly in the terminal -- no extra tools needed:

```bash
docker exec -it ignite-node1 /opt/ignite/apache-ignite/bin/sqlline.sh -u jdbc:ignite:thin://127.0.0.1:10800 -n "" -p ""
```

When prompted for a password just press Enter. You will see:

```
0: jdbc:ignite:thin://127.0.0.1:10800>
```

Paste any query and hit Enter. Type `!quit` to exit.

---

## Demo Script

### Step 1 -- Show the 3 nodes in the cluster
```sql
SELECT NODE_ID, CONSISTENT_ID FROM SYS.NODES;
```
Shows all 3 Docker containers operating as a single distributed cluster.

### Step 2 -- Show how Ignite partitioned the tables automatically
```sql
SELECT CACHE_NAME, CACHE_MODE
FROM SYS.CACHES
WHERE CACHE_TYPE = 'USER' AND CACHE_NAME != 'default';
```
Dimension tables are REPLICATED (full copy on every node for fast joins).
The fact table is PARTITIONED (rows automatically split across all 3 nodes).
Ignite decided this based on the WITH clause in the schema -- no manual configuration.

### Step 3 -- Run a distributed query
```sql
SELECT p.category, COUNT(*) AS transactions, ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.dim_product_id = p.id
GROUP BY p.category
ORDER BY total_revenue DESC;
```
Each node processes its own partition of fact_sales in parallel, joins locally
against its replicated copy of dim_product, then results are combined.

### Step 4 -- Fault tolerance demo
In a second terminal, stop a node while the cluster is running:
```bash
docker stop ignite-node2
```
Run the query from Step 3 again -- same results, same data. Ignite automatically
rerouted to backup partitions. Then bring it back:
```bash
docker start ignite-node2
```
Run Step 1 again to show node2 rejoined the cluster.

---

## All demo queries

See `queries/demo_queries.sql` for the full set of presentation queries including
monthly trends, top products, rush hour analysis, and loyalty vs walk-in breakdown.

---

## Stopping and Restarting

```bash
docker compose stop        # stops cluster, data stays in volumes
docker compose start       # restarts with data intact

docker compose down        # stops and removes containers
docker compose down -v     # stops and wipes all data (full reset)
```

---

## Project Structure

```
ignite-grocery-demo/
├── docker-compose.yml
├── config/
│   └── ignite-config.xml
├── init/
│   └── 01_schema.sql
├── data/
│   ├── fact_sales.sql
│   ├── dim_product.sql
│   ├── dim_customer.sql
│   ├── dim_time.sql
│   ├── dim_employee.sql
│   └── dim_payment_method.sql
├── queries/
│   └── demo_queries.sql
└── scripts/
    ├── load_data.py
    └── prepare_data.py
```
