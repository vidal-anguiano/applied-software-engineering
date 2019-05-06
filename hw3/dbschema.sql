DROP TABLE IF EXISTS ticket_sales;
CREATE TABLE ticket_sales (
t_id SERIAL PRIMARY KEY,
dt_sold DATE,
dt_ride DATE,
rdr_nme VARCHAR(20),
b_route VARCHAR(20),
status VARCHAR(20),
amnt_pd FLOAT
);
