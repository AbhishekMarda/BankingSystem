# Write your code here
import random
import sqlite3
# potential issue in the code: it does not take care of when randomly two card generations
# are the exact same. While the event is unlikely, it is still something that could happen
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("create table if not exists card(id integer, number text, pin text, balance integer default 0)")
conn.commit()


def create_string(size, value):
    str_val = str(value)
    while len(str_val) != size:
        str_val = "0" + str_val
    return str_val


def generate_checksum(first_15_acc_number):
    each_number = list(first_15_acc_number)
    luhn_sum = 0
    for i in range(len(each_number)):
        num = int(each_number[i])
        if (i + 1) % 2 == 1:
            num = 2 * num

        if num >= 10:
            num = num - 9
        luhn_sum = luhn_sum + num
    checksum = 10 - (luhn_sum % 10)
    if checksum == 10:
        checksum = 0
    return checksum


class Bank:
    IIN = 400000

    def __init__(self):
        self.pin = 0
        self.pin_string = ""
        self.account_identifier = 0
        self.identifier_string = ""
        self.balance = 0
        self.account_number = ""
        self.checksum = 0
        self.count = 0

    def create_account(self):
        self.pin = random.randint(0, 9999)
        self.account_identifier = random.randint(0, 999999999)
        self.pin_string = create_string(4, self.pin)
        self.identifier_string = create_string(9, self.account_identifier)
        self.account_number = str(self.IIN) + self.identifier_string
        self.checksum = generate_checksum(self.account_number)
        self.account_number = self.account_number + str(self.checksum)
        cur.execute(
            "insert into card values({}, {}, {}, {})".format(self.count + 1, self.account_number, self.pin_string, 0))
        conn.commit()

        # print the values
        print("\nYour card has been created")
        print("Your card number:")
        print(self.account_number)
        print("Your card PIN:")
        print(self.pin_string + "\n")

    def login(self, number, pin):
        cur.execute("select number, pin from card where number = {}".format(number))
        creds: list = cur.fetchone()

        if not creds:
            return False
        if creds[0] == number and create_string(4,creds[1]) == pin:

            self.account_number = number
            self.pin_string = pin
            cur.execute("select balance from card where number = {}".format(number))
            balance_list: list = cur.fetchone()
            self.balance = balance_list[0]
            return True
        else:
            return False

    def bal(self):
        return self.balance

    def change_bal(self, amt):
        self.balance = amt
        cur.execute("update card set balance = {} where number = {}".format(self.balance, self.account_number))
        conn.commit()

    def delete_account(self):
        cur.execute("delete from card where number = {}".format(self.account_number))
        conn.commit()

    def transfer(self, other_card_number):
        cur.execute("select balance from card where number = {}".format(other_card_number))
        bal_list = cur.fetchone()
        if not bal_list:
            print("Such a card does not exist.\n")
        else:
            print("Enter how much money you want to transfer:")
            amt = int(input())
            if amt > self.balance or amt < 0:
                print("Not enough money!\n")
            else:

                bal = int(bal_list[0]) + amt
                self.balance = self.balance - amt
                cur.execute("update card set balance = {} where number = {}".format(self.balance, self.account_number))
                cur.execute("update card set balance = {} where number = {}".format(bal, other_card_number))
                print("Success!\n")
        conn.commit()
# todo: con.commit

# END OF CLASS DEFINITION

bank = Bank()

while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    input_option = int(input())

    if input_option == 0:
        print("\nBye!")
        break

    elif input_option == 1:
        bank.create_account()

    elif input_option == 2:
        print("\nEnter your card number:")
        number = input()
        print("Enter your PIN:")
        pin = input()

        if not bank.login(number, pin):
            print("\nWrong card number or PIN!\n")

        else:
            print("\nYou have successfully logged in!\n")
            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                input_op = int(input())

                if input_op == 1:
                    rem = bank.bal()
                    print(f"\nBalance: {str(rem)}\n")

                elif input_op == 2:
                    print("\nEnter income:")
                    income = int(input())
                    bank.change_bal(bank.balance + income)
                    print("Income was added!\n")
                # fixme
                elif input_op == 3:
                    print("\nTransfer")
                    print("Enter card number:")
                    other_card = input()
                    checksum = generate_checksum(other_card[0:15])
                    if other_card == bank.account_number:
                        print("You can't transfer money to the same account!\n")
                    elif checksum != int(other_card[15]):
                        print("Probably you made a mistake in the card number. Please try again!\n")
                    else:
                        bank.transfer(other_card)

                elif input_op == 4:
                    bank.delete_account()
                    print("\nThe account has been closed!\n")
                    break

                elif input_op == 5:
                    print("\nYou have successfully logged out\n")
                    break

                elif input_op == 0:
                    print("\nBye!")
                    exit()
    elif input_option == 5:
         for row in cur.execute("select * from card"):
             print(row)

