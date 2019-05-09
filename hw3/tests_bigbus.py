import datetime as dt

import pytest
import psycopg2
import sqlalchemy

from bigbus import UserInt, Seller, DBSess, Refund, get_dates_10d_out
from bigbus_orm import Tickets

EXAMPLE_SALES = [{'ride_date': '07-01-2019',
                  'bus_route': 'red',
                  'ticket_quant': 2,
                  'rider_name': 'test_case'},
                  {'ride_date': '07-02-2019',
                   'bus_route': 'blue',
                   'ticket_quant': 4,
                   'rider_name': 'test_case'}]

dbsess = DBSess().getInstance()

@pytest.mark.parametrize('command', ['Sell', 'Issue Refund', 'Report', 'Quit'])
def test_is_valid_command(command):
    userint = UserInt()
    assert userint.is_valid_command(command)


def test_date_select_within_10days():
    next_10_days = get_dates_10d_out()
    assert len(next_10_days) == 10

    next_day =  (dt.datetime.today() + dt.timedelta(days=1)).strftime('%m-%d-%Y')
    assert next_day in next_10_days


def test_get_ride_and_rider_details():
    seller = Seller()
    details = EXAMPLE_SALES[0]
    seller.collect_ticket_sale_details(test=True, details=details)

    assert seller.ride_date
    assert seller.bus_route
    assert seller.ticket_quant
    assert seller.rider_name


def test_create_tickets_from_sale_details():
    seller = Seller()
    details = EXAMPLE_SALES[0]
    seller.collect_ticket_sale_details(test=True, details=details)
    seller.prepare_tickets()

    assert len(seller.tickets) == details['ticket_quant']
    assert seller.tickets[0]['rider_name'] == details['rider_name']


def test_ticket_sale_processes_successfully():
    seller = Seller()
    details = EXAMPLE_SALES[1]
    seller.collect_ticket_sale_details(test=True, details=details)
    seller.prepare_tickets()
    seller.process_sale(dbsess)

    results = dbsess.query(Tickets)\
                    .filter(Tickets.rider_name == 'test_case')\
                    .filter(Tickets.ride_date == '07-02-2019')\
                    .filter(Tickets.bus_route == 'blue')\
                    .all()

    ticket = results[0]

    assert len(results) % 4 == 0
    assert ticket.rider_name == 'test_case'
    assert ticket.ride_date == dt.datetime.strptime('07-02-2019', '%m-%d-%Y').date()
    assert ticket.bus_route == 'blue'


def test_get_refund_details():
    refund = Refund()
    details = EXAMPLE_SALES[1]
    refund.collect_refund_details(test=True, details=details)

    assert refund.rider_name
    assert refund.bus_route
    assert refund.ride_date
