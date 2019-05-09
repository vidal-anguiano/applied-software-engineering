DROP TABLE IF EXISTS ticket_sales;
CREATE TABLE ticket_sales (
t_id SERIAL PRIMARY KEY,
date_sold DATE,
ride_date DATE,
rider_name VARCHAR(20),
bus_route VARCHAR(20),
status VARCHAR(20),
amount_paid FLOAT
);
