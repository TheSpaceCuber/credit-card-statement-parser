from itertools import chain
import datetime
import csv
import pandas as pd

def extract_year(pages) -> int:
    '''
    Extracts the year from the pdf statement
    '''
    year = -1
    for page in pages:
        page_text = page.extract_text()
        lines = page_text.split()
        for line in lines:
            if line.startswith('StatementDate:'):
                year = int(line[-4:])
    return year

def get_transactions(pages) -> list:
    '''
    Extracts the raw transactions from the pdf statement
    '''
    transactions = []
    for page in pages:
        page_text = page.extract_text()
        lines = page_text.split('DATE DESCRIPTION AMOUNT(SGD)')
        if len(lines) > 1:
            transactions.append(lines[1].split('\n'))
    return transactions

def process_transactions(raw_transactions, current_year) -> list:
    '''
    Converts the raw transactions into a clean list of transactions
    '''
    # flatten
    transactions = list(chain.from_iterable(raw_transactions))
    
    # remove empty strings
    transactions = list(filter(None, transactions))
    
    # remove the first few lines that are not transactions
    transactions = transactions[6:]
    
    # remove those XXXX
    transactions = list(filter(lambda x : not x.startswith('XXXX'), transactions))
    
    # remove the last few lines that are not transactions
    transactions = transactions[:-16]
    
    # Create an empty list to store the formatted data
    formatted_transactions = []

    # Iterate through the original data and format it
    for item in transactions:
        # Split the item into date, description, and amount
        print(item)
        parts = item.split()
        date_str = f"{parts[0]} {current_year}"
        date = datetime.datetime.strptime(date_str, '%d%b %Y')
        price = parts[-1]
        if price.startswith('('):
            price = price[1:-1]
        desc = parts[1:-1]
        formatted_transactions.append([date, price, ''.join(desc)])
        
    return formatted_transactions

def get_masterlist(filepath) -> list:
    masterlist = []
    with open(filepath) as file_obj:
        reader_obj = csv.reader(file_obj) 
        for row in reader_obj:
            masterlist.append(row)
    masterlist = masterlist[1:]
    return masterlist

def convert_transactions_to_dataframe(formatted_transactions, masterlist):
    dataframe_list = []
    for transaction in formatted_transactions:
        date = transaction[0]
        original_desc = transaction[2]
        price = transaction[1]
        # print(original_desc)
        for entry in masterlist:
            cleaned_desc = entry[0]
            category = entry[1]
            if cleaned_desc in original_desc:
                dataframe_list.append([date, cleaned_desc, category, price])

    df = pd.DataFrame(dataframe_list, columns = ['Date', 'Transaction Name', 'Category', 'Price'])
    df['Price'] = df['Price'].astype(float)
    df['Transaction Name'] = df['Transaction Name'].astype(str)
    df['Category'] = df['Category'].astype(str)
    return df