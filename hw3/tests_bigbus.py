import datetime as dt

import pytest

from bigbus import UserInt, Seller, get_dates_10d_out

@pytest.mark.parametrize('command', ['Sell', 'Issue Refund', 'Report', 'Quit'])
def test_is_valid_command(command):
    userint = UserInt()
    assert userint.is_valid_command(command)


def test_date_select_within_10days():
    next_10_days = get_dates_10d_out()
    assert len(next_10_days) == 10

    next_day =  (dt.datetime.today() + dt.timedelta(days=1)).strftime('%m-%d-%Y')
    assert next_day in next_10_days


def test_get_ride_and_rider_info():
    seller = Seller()
    details = {'ride_date': '07-01-2019',
               'bus_route': 'red',
               'ticket_quant': 2,
               'rider_name': 'test_case'}
    seller.collect_ticket_sale_details(test=True, details=details)

    assert seller.ride_date
    assert seller.bus_route
    assert seller.ticket_quant
    assert seller.rider_name
