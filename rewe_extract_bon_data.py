import PyPDF2
import pandas as pd
import re

from datetime import date

#used for testing
#REWE_BON = 'Rewe/Dein REWE eBon vom 28.11.2022.pdf'

def read_pdf_info(pdf):
    pdf_file = open(pdf, 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    page = read_pdf.getPage(0)
    page_content = page.extractText()
    return page_content

def clean_rewe_bon(page_content):
    payment = 0 #check if card was used in payment
    date_payment = 0 #check if date was added correctly
    groceries = []
    table_list = page_content.split('\n')
    for index, grocery in enumerate(table_list):
        if ',' in grocery:# and '%' not in grocery:
            grocery_item = grocery.split('  ')
            groceries.append(grocery_item)
        if 'Bezahlung' in grocery:
            groceries.append(['Payment: '+table_list[index+2].strip()])
            payment = payment + 1
        if 'Datum' in grocery:
            groceries.append([grocery.replace(' ', '')])
    if payment == 0:
        groceries.append(['Payment: Cash'])
    if date_payment == 0:
        today = date.today()
        today = today.strftime('%d.%m.%Y')
        groceries.append(['Datum:' + today])
    return groceries

def create_df(grocery_list):
    grocery_items = [[item for item in grocery if item] for grocery in grocery_list] #remove any empty strings

    try:
        payment_type = []
        for grocery in grocery_list:
            for item in grocery:
                if 'Payment: ' in item:
                    payment_type.append(item)
        payment_type = payment_type[0].lstrip('Payment: ')
    except IndexError:
        payment_type = 'not known'
        
    try:
        date_bought = []
        for date in grocery_list:
            for item in date:
                if 'Datum:' in item:
                    date_bought.append(item)
        date_bought = date_bought[0].lstrip('Datum:')
    except IndexError:
        date_bought = 'unknown'
    
    summe_index = [] #find index of summe list to minimize list
    summe_price = []
    for index, grocery in enumerate(grocery_items):
        for item in grocery:
            if 'SUMME' in item:
                summe_index.append(index)
                summe_price.append(grocery)
                break

    #print(summe_price, float(summe_price[0][2].replace(',','.')))
    grocery_name = []
    grocery_price = []
    grocery_count = []
    
    for grocery in grocery_items[:summe_index[0]]:
        grocery[0] = grocery[0].strip()
        grocery[1] = grocery[1].strip()
        weighted_input = re.findall(r'.+EUR/kg', grocery[1]) #remove weighted groceries
        handeingabe = re.findall(r'.*Handeingabe E-Bon.*', grocery[0]) #remove manual input for groceries (e.g from butcher)
        more_than_one_item = re.findall(r'.*Stk x', grocery[0]) #remove more than 1 bought items
        if len(weighted_input) == 0 and len(handeingabe) == 0:
            if len(more_than_one_item) == 0:
                grocery_name.append(grocery[0])
                grocery_price.append(grocery[1])
                grocery_count.append(1)
            elif len(more_than_one_item) > 0:
                number_of_bought_items = re.split(r'\s', grocery[0])
                grocery_count[-1] = number_of_bought_items[0]
                
    #set up the dataframe
    data = {'grocery_name': grocery_name, 
            'grocery_price': grocery_price, 
            'grocery_count': grocery_count, 
            'payment_type': payment_type, 
            'date_of_purchase': date_bought,
            'store_bought_at': 'REWE'}
    
    #create dataframe
    df = pd.DataFrame(data=data)
    return df

def clean_df(df):
    df['grocery_price'] = df['grocery_price'].str.replace(r'B|A|\*', '').str.strip().str.replace(',','.').astype('float')
    df['grocery_count'] = df['grocery_count'].astype('int')

    try:
        df['date_of_purchase'] = pd.to_datetime(df['date_of_purchase'], dayfirst = True).dt.strftime('%d.%m.%Y')
        df['weekday_purchased'] = pd.to_datetime(df['date_of_purchase'], dayfirst = True).dt.strftime('%A')
    except ValueError:
        pass
    return df

def check_final_price(cleaned_df, cleaned_bon):
    sum_price = []
    for grocery in cleaned_bon:
        for item in grocery:
            if 'SUMME' in item:
                sum_price.append(grocery)
                break
    
    sum_price_raw = round(float(sum_price[0][-1].replace(',','.')), 2) 
    sum_price_df = round(cleaned_df['grocery_price'].sum(), 2)
    
    if sum_price_raw == sum_price_df: #all good if both sums are same
        cleaned_df['check'] = 'passed'
        return [cleaned_df, sum_price_df]
    
    elif sum_price_raw != sum_price_df: #problem if both sums are not the same
        missing_sum = sum_price_raw - sum_price_df #find missing sum
        new_row = {'grocery_name': ['missing_input'], #add new row with missing input
            'grocery_price': [missing_sum], 
            'grocery_count': ['1'], 
            'payment_type': [cleaned_df.iloc[0,3]], 
            'date_of_purchase': [cleaned_df.iloc[0,4]],
            'store_bought_at': ['REWE'],
            'weekday_purchased': [cleaned_df.iloc[0,6]]}
        new_df = pd.DataFrame(data=new_row)
        cleaned_df = pd.concat([cleaned_df, new_df], ignore_index = True)
        cleaned_df['check'] = 'not passed' #add column with not passed
        return [cleaned_df, sum_price_raw]
    
def executer(original_bon):
    pdf_info = read_pdf_info(original_bon)
    rewe_bon = clean_rewe_bon(pdf_info)
    initial_df = create_df(rewe_bon)
    cleaned_df = clean_df(initial_df)
    final_df = check_final_price(cleaned_df, rewe_bon)
    return final_df
    

#executer(REWE_BON)
