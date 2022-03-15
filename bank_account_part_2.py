#python -m pip install mysql-connector-python
#python -m pip install mysql

import mysql.connector
from mysql.connector import errorcode
import time
'''
@author Ryan Slivinski
@date Dec. 2, 2020

CSE4701 - Principles of Databases
Project 2
'''
class Bank:       
    def __init__(self):
        self.cnx = None
        self.cur = None
        self.dbConnect()
        
    ''' database methods start here--- '''
    def dbConnect(self):
        self.config = {
            'user': 'root',
            'password': 'spiral_lass_lid',
            'host': 'localhost',
            'database': 'cse4701f20_project2',
            'raise_on_warnings': True
        }
        
        self.cnx = None
        self.cur = None
        try:
            self.cnx = mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Invalid username/password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Invalid database")
            else:
                print(err)

        self.cur = self.cnx.cursor(named_tuple=True, buffered=True)

    def dbClose(self):
        self.cnx.close()

    def runSQL(self, sql, data=None):
        self.cur.execute(sql, data)

    def fetch(self):
        return self.cur.fetchone()

    def lastRowId(self):
        return self.cur.lastrowid

    def commit(self):
        self.cnx.commit()
        
    ''' --- database methods end here ---'''

    '''
    Get details on a particular account.
    Lock the account when required
    (i.e. when lock parameter is supplied with a 'True' value)
    '''
    def getAccount(self, acct_num, lock=False):
        if acct_num is None:
            raise Exception('Account number missing')

        sql = (
            "SELECT * FROM account"
            " WHERE account_no = %s"
            )
        
        if lock:
            sql += " FOR UPDATE"
                        
        data = (acct_num,)
        self.runSQL(sql, data)
        row = self.fetch()
        if row is None:
            raise Exception("Account #" + str(acct_num) + " does not exist")

        account = {}
        account['acct_num'] = acct_num
        account['name_on_account'] = row.name_on_account
        account['balance'] = row.balance
        account['account_open_date'] = row.account_open_date
        account['account_status'] = row.account_status
        return account

    def showAccount(self, account):    
        print("Account number:", account['acct_num'])
        print("Name on account:", account['name_on_account'])
        print("Balance:", account['balance'])
        print("Account opened on:", account['account_open_date'])
        print("Account status:", account['account_status'])        

    def openAccount(self):
        print()
        name = input("Name on account: ")
        balance = float(input("Enter Initial Balance: "))
        if balance < 0:
            raise Exception("Initial balance cannot be negative")
        sql = (
          "INSERT INTO account(name_on_account, balance)"
          " VALUES (%s, %s)"
        )
        data = (name, balance)       
        self.runSQL(sql, data)
        
        acct_num = self.lastRowId()
        self.commit()
        print()
        print("---Account successfully created---")
        account = self.getAccount(acct_num)
        self.showAccount(account)
        print("------")
        return acct_num
        
    def checkBalance(self):
        # returns the balance of the account        
        try:
            print()
            print('Checking account balance')
            acct_num = int(input("Enter account number: "))
        except ValueError:
            raise Exception("Invalid account number")
        print()
        print("---Checking account balance---")
        account = self.getAccount(acct_num)
        self.showAccount(account)
        print("------")
        return account
        
    def closeAccount(self):
        try:
            print()
            print('Closing account')
            acct_num = int(input("Enter account number: "))
        except ValueError:
            raise Exception("Invalid account number")
        print()
        print("---Checking account status---")
        account = self.getAccount(acct_num)
        self.showAccount(account)
        if account['account_status'] == 'closed':
            raise Exception("This account is already closed")
        
        print()
        confirmation = input("Are you sure about closing this account? Y/N ")
        if confirmation == 'Y':
            print("CONFIRMED")
            sql = (
                "UPDATE account"
                " SET account_status='closed'"
                " WHERE account_no= %s "
                )
            data = (acct_num,)
            self.runSQL(sql, data)
            self.commit()
            print("Account#", acct_num, "successfully closed")
        else:
            print("CANCELLED")
            return

    def deposit(self):
        try:
            print()
            acct_num = int(input("Enter account number: "))
        except ValueError:
            raise Exception("Invalid account number")
        
        print()
        account = self.getAccount(acct_num, lock=True)
        self.showAccount(account)
        print()
        amount = float(input("Enter desposit amount: "))
        cur_bal = account['balance']
        new_bal = amount + cur_bal
        sql = (
            "UPDATE account"
            " SET balance = %s"
            " WHERE account_no = %s"
        )
        print()
        print("Depositing funds...")
        time.sleep(5)
        data = (new_bal, acct_num,)
        self.runSQL(sql, data)
        self.commit()
        print()
        print("New balance:", new_bal)

    def withdraw(self):
        '''
            - ask for account number
            - show account details
            - lock account for update
            - ask for withdraw amount
            - update balance
            - release lock
            - show new balance
            - display error if balance is insufficient for withdrawal
        '''
        try:
            print()
            acct_num = int(input("Enter account number: "))
        except ValueError:
            raise Exception("Invalid account number")

        print()
        account = self.getAccount(acct_num, lock=True)
        self.showAccount(account)
        print()
        amount = float(input("Enter withdraw amount: "))
        cur_bal = account['balance']
        if amount > cur_bal:
            raise Exception("Insufficient Funds")
        new_bal = cur_bal - amount
        sql = (
            "UPDATE account"
            " SET balance = %s"
            " WHERE account_no = %s"
        )
        print()
        print("Withdrawing funds...")
        time.sleep(5)
        data = (new_bal, acct_num,)
        self.runSQL(sql, data)
        self.commit()
        print()
        print("New balance:", new_bal)

    def transfer(self):
        try:
            print()
            src_acct_num = int(input("Enter source account number: "))
        except ValueError:
            raise Exception("Invalid account number")

        print()
        src_account = self.getAccount(src_acct_num, lock=True)
        self.showAccount(src_account)
        print()

        try:
            print()
            trgt_acct_num = int(input("Enter target account number: "))
        except ValueError:
            raise Exception("Invalid account number")

        print()
        trgt_account = self.getAccount(trgt_acct_num, lock=True)
        self.showAccount(trgt_account)
        print()

        transfer_amt = float(input("Enter transfer amount: "))
        cur_src_bal = src_account['balance']

        if transfer_amt > cur_src_bal:
            raise Exception("Insufficient funds.")

        new_src_bal = cur_src_bal - transfer_amt
        src_sql = (
            "UPDATE account"
            " SET balance = %s"
            " WHERE account_no = %s"
        )
        src_data = (new_src_bal, src_acct_num,)
        self.runSQL(src_sql, src_data)
        # self.commit()
        print()
        print('Withdrawing from source account...')
        print()
        time.sleep(10)

        cur_trgt_bal = trgt_account['balance']
        new_trgt_bal = cur_trgt_bal + transfer_amt

        trgt_sql = (
            "UPDATE account"
            " SET balance = %s"
            " WHERE account_no = %s"
        )
        trgt_data = (new_trgt_bal, trgt_acct_num,)
        self.runSQL(trgt_sql, trgt_data)
        self.commit()
        print()
        print('Depositing into target account...')
        print()
        time.sleep(10)
        print("Transfer successful.")

def main():
    bank = Bank()
    op = 1
    while op != 0:
        try:
            print()
            print("Main Menu")
            print("[0] - Quit")
            print("[1] - Open Account")
            print("[2] - Check Balance")
            print("[3] - Close Account")
            print("[4] - Deposit")
            print("[5] - Withdraw")
            print("[6] - Transfer")
            op = int(input("Enter your choice: "))
            if op == 1:
                bank.openAccount()
            elif op == 2:
                bank.checkBalance()
            elif op == 3:
                bank.closeAccount()
            elif op == 4:
                bank.deposit()
            elif op == 5:
                bank.withdraw()
            elif op == 6:
                bank.transfer()
            elif op == 0:
                print()
                print("Thank you for using Slivinski Bank.")
                break

        except Exception as error:
            print('--------')
            print('Error:', error)
            print('--------')
        
if __name__ == '__main__':
    main()
