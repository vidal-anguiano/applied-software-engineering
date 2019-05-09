import yaml
import datetime as dt
from abc import ABC, abstractmethod

import inquirer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from bigbus_orm import Tickets

CONFIG = yaml.safe_load(open('./config.yml','r'))

PRICES = CONFIG['prices']
CAPACITY = CONFIG['capacity']
MAXSEATS = CONFIG['max_seats']

class UserInt():
    _instan = None
    _active = None

    def __init__(self):
        '''Initializes singleton UserInt.'''
        if not UserInt._instan:
            UserInt._instan = self
            UserInt._active = True
            self._seller = Seller()
            self._refund = Refund()
            self._report = Report()
            self._dbsess = DBSess().getInstance()

        else:
            print("Already created a UserInt!")


    def run(self):
        while UserInt._active:
            tag = 'action'
            message = 'What would you like to do?'
            choices = ['Sell',
                       'Issue Refund',
                       'Report',
                       'Quit',]

            run_command = list_prompt_and_response(tag, message, choices)

            assert self.is_valid_command(run_command), "Not a valid command."

            if run_command == 'Sell':
                self._seller.collect_ticket_sale_details()
                self._seller.prepare_tickets()
                self._seller.process_sale(self._dbsess)

            if run_command == 'Issue Refund':
                self._refund.r_name()
                self._refund.r_route()
                self._refund.r_date()
                self._refund.r_cnfrm()
                self._refund.r_prces(self._dbsess)

            if run_command == 'Report':
                self._report.r_date()
                self._report.gen_rpt(self._dbsess)

            if run_command == 'Quit':
                UserInt._active = False


    def is_valid_command(self, command):
        commands = ["Sell",
                    "Issue Refund",
                    "Report",
                    "Quit"]
        return command in commands


class Seller():

    def __init__(self):
        self.today = dt.datetime.today().strftime('%m-%d-%Y')
        self.ride_date = None
        self.bus_route = None
        self.ticket_quant = None
        self.rider_name = None

    def collect_ticket_sale_details(self, test=False, details=None):
        if test:
            details = details
        else:
            details = {'ride_date': self.ask_ride_date(),
                       'bus_route': self.ask_bus_route(),
                       'ticket_quant': self.ask_ticket_quant(),
                       'rider_name': self.ask_rider_name()}

        self.ride_date = details['ride_date']
        self.bus_route = details['bus_route']
        self.ticket_quant = details['ticket_quant']
        self.rider_name = details['rider_name']


    def ask_ride_date(self):
        tag = 'date'
        message = 'For which date would you like to sell a ticket?'
        choices = get_dates_10d_out()
        return list_prompt_and_response(tag, message, choices)


    def ask_bus_route(self):
        tag = 'bus'
        message = 'Which route would you like to ride?'
        choices = ['Red',
                   'Blue',
                   'Green']
        return list_prompt_and_response(tag, message, choices)


    def ask_ticket_quant(self):
        tag = 'quant'
        message = 'How many tickets would you like to purchase?'
        choices = [1,2,3,4]
        return list_prompt_and_response(tag, message, choices)


    def ask_rider_name(self):
        nprompt = [inquirer.Text('name',
                                 message='Name of purchaser?')]
        return inquirer.prompt(nprompt)['name']


    def prepare_tickets(self):
        self.tickets = [{'date_sold': self.today,
                     'ride_date': self.ride_date,
                     'rider_name': self.rider_name,
                     'bus_route': self.bus_route,
                     'status': 'Active'} for _ in range(self.ticket_quant)]


    def process_sale(self, dbsess):
        ticket_quant = len(self.tickets)
        ticket = self.tickets[0]
        price = PRICES[wkday(ticket['ride_date'])]
        route = ticket['bus_route'].lower()
        ride_date = ticket['ride_date']

        if self._at_capacity(ride_date, route, dbsess):
            for ticket in self.tickets:
                #price = PRICES[wkday(ticket['dt_ride'])]
                dbsess.add(Tickets(date_sold = ticket['date_sold'],
                                   ride_date = ticket['ride_date'],
                                   rider_name = ticket['rider_name'],
                                   bus_route = ticket['bus_route'].lower(),
                                   status =  ticket['status'],
                                   amount_paid = price if ticket_quant < 4 else price*.9))
                dbsess.commit()
        else:
            print(f"I'm sorry, there are no longer any seats available on the {route} route.")


    def _at_capacity(self, ride_date, route, dbsess):
        ride_date = dt.datetime.strptime(ride_date, '%m-%d-%Y').date()
        result = dbsess.query(func.count(Tickets.t_id))\
                       .filter(Tickets.status == 'Active')\
                       .filter(Tickets.ride_date == ride_date)\
                       .all()
        tickets_sold = result[0][0]

        return tickets_sold < MAXSEATS*CAPACITY[route]


class Refund():

    def __init__(self):
        self.rider_name = None
        self.bus_route = None
        self.ride_date = None
        self.confirm = None


    def collect_refund_details(self, test=False, details=None):
        if test:
            details = details
        else:
            details = {'rider_name': self.ask_rider_name(),
                       'bus_route': self.ask_bus_route(),
                       'ride_date': self.ask_ride_date()}
        self.rider_name = details['rider_name']
        self.bus_route = details['bus_route']
        self.ride_date = details['ride_date']


    def ask_rider_name(self):
        prompt = [inquirer.Text('name',
                                 message='What is the name listed on the ticket purchase?')]

        self.rider_name = inquirer.prompt(prompt)['name']


    def ask_bus_route(self):
        prompt = [inquirer.List('route',
                                 message='Which route did you buy your tickets for?',
                                 choices=['Red',
                                          'Blue',
                                          'Green'])]

        self.bus_route = inquirer.prompt(prompt)['route'].lower()


    def ask_ride_date(self):
        prompt = [inquirer.Text('date',
                                 message='For which date were the tickets purchased?')]

        self.ride_date = inquirer.prompt(prompt)['date']


    def ask_to_confirm(self):

        cprompt = [inquirer.Confirm('confirm', message=f'Process refund for {self.rdr_nme}\'s, tickets on the {self.b_route} route for {self.dt_ride}?')]
        self.confirm = inquirer.prompt(cprompt)['confirm']


    def process_refund(self, dbsess):
        self.dt_ride = dt.datetime.strptime(self.dt_ride, '%m-%d-%Y').date()

        if self.confirm:
            dbsess.query(Tickets)\
                   .filter(Tickets.rdr_nme == self.rdr_nme)\
                   .filter(Tickets.dt_ride == self.dt_ride)\
                   .filter(Tickets.b_route == self.b_route)\
                   .filter(Tickets.status == 'Active')\
                   .update({Tickets.status: 'Refunded'}, synchronize_session='evaluate')

            dbsess.commit()


class DBSess():
    '''
    Singleton database connection.
    '''
    _engine = create_engine('postgresql:///bigbus')
    _sessionmaker = sessionmaker(bind=_engine)
    _dbsess = None

    def __init__(self):
        if not DBSess._dbsess:
            DBSess._dbsess =  self._sessionmaker()

    def getInstance(self):
        return DBSess._dbsess


def wkday(dt_str):
    days = {0:'Monday',
            1:'Tuesday',
            2:'Wednesday',
            3:'Thursday',
            4:'Friday',
            5:'Saturday',
            6:'Sunday'}

    day = dt.datetime.strptime(dt_str, '%m-%d-%Y').weekday()

    return days[day]


class Report():
    def __init__(self):
        self.dt_ride = None


    def r_date(self):
        dprompt = [inquirer.Text('date',
                                 message='For which date do you want to generate a report?')]

        self.dt_ride = inquirer.prompt(dprompt)['date']

    def gen_rpt(self, dbsess):
        self.dt_ride = dt.datetime.strptime(self.dt_ride, '%m-%d-%Y').date()

        counts = dbsess.query(func.count(Tickets.t_id),
                              Tickets.b_route)\
                       .filter(Tickets.dt_ride == self.dt_ride)\
                       .filter(Tickets.status == 'Active')\
                       .group_by(Tickets.b_route)\
                       .all()

        print('\n'*2,
              f"Ticket sales report for {self.dt_ride}:\n",
              "\n".join([str((i[1],i[0])) for i in counts]),
              '\n'*2)


def list_prompt_and_response(tag, message, choices):
    prompt = [inquirer.List(tag,
                            message,
                            choices)]
    response = inquirer.prompt(prompt)[tag]
    return response


def get_dates_10d_out():
    today = dt.datetime.today()
    days = [(today + dt.timedelta(days=i)).strftime('%m-%d-%Y') for i in range(1,11)]
    return days


if __name__ == '__main__':
    userint = UserInt()
    userint.run()
