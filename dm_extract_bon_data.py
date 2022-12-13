import PyPDF2
import pandas as pd
import re

#used for testing
#DM_BON = 'DM/dm-eBon_2022-10-25_10-26-53.pdf'

def read_pdf_info(pdf):
    pdf_file = open(pdf, 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    page = read_pdf.getPage(0)
    page_content = page.extractText()
    return page_content

"""
The goal is to clean up the pdf and take out most of the unecessary information
Input: The pdf
Output: A list with the most important information
"""

def clean_dm_bon(page_content):
    groceries = []
    raw_table_list = page_content.split('\n')
    find_index_sum = [index for index, item in enumerate(raw_table_list) if 'SUMME EUR' in item] #find index of sum
    table_list = raw_table_list[3:find_index_sum[0]+1] 
    for grocery in table_list:
        if grocery not in ['Brutto', 'rabattfähige Artikel', 'Nr. XX', 'neuer Wert', 'Zwischensumme']:
            grocery_item = re.split(r'\s{2,}', grocery) #different method used than rewe_extract
            groceries.append(grocery_item)
    for index, grocery in enumerate(raw_table_list):
        if 'TA-Nr' in grocery:
            groceries.append(['Payment: '+raw_table_list[index+2].strip()])
        if 'Datum' in grocery:
            groceries.append([grocery.replace('  ', '')])
    return groceries

"""
The goal is to clean up the provided list, add any missing information and creating a dataframe
Input: A list object
Output: A Pandas Dataframe
"""

def create_df(grocery_list):
    payment_type = []
    for grocery in grocery_list:
        for item in grocery:
            if 'Payment: ' in item:
                payment_type.append(item)
    payment_type = payment_type[0].lstrip('Payment: ')
    
    date_bought = []
    for date in grocery_list:
        for item in date:
            if 'Datum' in item:
                date_bought.append(item)
    date_bought = date_bought[0].lstrip('Datum:').rstrip(' Uhr')

    grocery_name = []
    grocery_price = []
    grocery_count = []
    
    grocery_items = [[item for item in grocery if item] for grocery in grocery_list]
    for grocery in grocery_items:
        if len(grocery) == 4:
            grocery[0] = grocery[0] + ' ' + grocery[1]
            del(grocery[1])
        for index, item in enumerate(grocery):
            item = item.strip()
            if index == 0 and len(grocery) == 3:
                grocery_name.append(item)
            if index == 1 and len(grocery) == 3:
                grocery_price.append(item)
            if index == 2 and len(grocery) == 3:
                grocery_count.append(item)
            if len(grocery) == 2 and 'dm-Geschenkkarte' in item:
                grocery[1] = grocery[1].replace(' §5','')
                grocery.append('1')
                if index == 0:
                    grocery_name.append(item)
                if index == 1:
                    grocery_price.append(item)
                if index == 2:
                    grocery_count.append(item)
    
    data = {'grocery_name': grocery_name, 
            'grocery_price': grocery_price, 
            'grocery_count': grocery_count, 
            'payment_type': payment_type, 
            'date_of_purchase': date_bought,
            'store_bought_at': 'DM'}
    
    df = pd.DataFrame(data=data)
    return df

""" 
The goal is to clean up the dataframe by defining the correct datatypes and making these readable for the correct datatype
Input: Pandas Dataframe
Output: Pandas Dataframe
"""

def clean_df(df):
    df['grocery_price'] = df['grocery_price'].str.replace(',','.').astype('float')
    df['grocery_count'] = df['grocery_count'].astype('int')
    df['date_of_purchase'] = pd.to_datetime(df['date_of_purchase'], dayfirst=True).dt.strftime('%d.%m.%Y')
    df['weekday_purchased'] = pd.to_datetime(df['date_of_purchase'], dayfirst=True).dt.strftime('%A')
    return df

""" 
The goal is to check if the final price is correct by taking the sum out of the receipt and sum from the grocery price. If the price is correct, all is good.
If the price is incorrect, a missing input row is added
Input: Pandas Dataframe
Output: List with Pandas Dataframe and final sum
"""

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
            'store_bought_at': ['DM'],
            'weekday_purchased': [cleaned_df.iloc[0,6]]}
        new_df = pd.DataFrame(data=new_row) # create new dataframe with row
        cleaned_df = pd.concat([cleaned_df, new_df], ignore_index = True) #concat cleaned df with new df
        cleaned_df['check'] = 'not passed' #add column with not passed, as the sum did not match
        return [cleaned_df, sum_price_raw]

def executer(original_bon):
    pdf_info = read_pdf_info(original_bon)
    dm_bon = clean_dm_bon(pdf_info)
    initial_df = create_df(dm_bon)
    cleaned_df = clean_df(initial_df)
    final_df = check_final_price(cleaned_df, dm_bon)
    return final_df