# Big Bus Implementation

## Setup 

### Required Software Installations
- Python 3.6+
- PostgreSQL

### Required Python Packages
- sqlalchemy
- pyyaml
- inquirer
- psycopg2-binary

### Setup Database
If you have PostgreSQL installed, you should be able to run `bash setup.sh` to create the `bigbus` database and create the required table.


### Running the Program
You can run the program by running `python bigbus.py`.

#### To sell a ticket...
Select "Sell" from the main menu and:  
1. Select a date  
2. Select a route  
3. Select a quantity  
4. Input a name  
      
#### To process a refund...
Select "Issue Refund" from the main menu and:  
1. Input name on the reservation  
2. Select the route  
3. Input the date in the `m-d-Y` format. The current implementation assumes the user inputs a date in this format    
4. Confirm refund by hitting `y`  

If there aren't any tickets that are active for the name and date given, nothing will happen.  

#### To see a report of sold tickets...  
Select "Report" from the main menu and:  
1. Input the date in the `m-d-Y` format


### Other Assumptions and Simplifications
To reiterate, any request for a date assumes the user will input a date in the `m-d-Y` format. For any tickets sold, the `status` of the ticket in the database is listed as `Active`. If the ticket is refunded, then the status changes to `Refunded`. Also, no name need be provided to make a ticket sale.


