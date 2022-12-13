from PIL import Image
from pytesseract import pytesseract

import re
import pandas as pd

#used for testing purposes
#LIDL_BON = 'LIDL/LIDL8_discount.png'
COUNTING = 0
LIDL_SUM = [111.19] #LIDL sums need to be added mannually as LIDL only provides images that are sometimes incorrectly interpreted by the ML algorithm


def read_png_text(png_file):
    #Define path to tessaract.exe
    path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    #Define path to image
    path_to_image = png_file

    #Point tessaract_cmd to tessaract.exe
    pytesseract.tesseract_cmd = path_to_tesseract

    #Open image with PIL
    img = Image.open(path_to_image)

    #Extract text from image
    page_content = pytesseract.image_to_string(img)
    return page_content

def clean_lidl_bon(page_content):
    #clean page content
    raw_table_list = page_content.split('\n')
    find_index_sum = [index for index, item in enumerate(raw_table_list) if 'Summe' in item] #find index of sum
    find_index_Bonkopie = [index for index, item in enumerate(raw_table_list) if 'Bonkopie' in item] #find index of sum
    table_list = raw_table_list[find_index_Bonkopie[0]:find_index_sum[0]+1] #limit the list to less options for the following loop
    groceries = []
    
    #find grocery items plus price and number of items bought if available
    for grocery in table_list:
        if re.findall(r'.,[0-9]{2}\s[A|B]', grocery): #find all the items bought
            grocery_items = re.split(r'\s', grocery)
            if re.findall(r'[A|B]', grocery_items[-1]):
                    del(grocery_items[-1]) #remove letter a or b from last place
            if len(grocery_items) > 2:
                length_grocery = len(grocery_items)-1
                grocery_items[0:length_grocery] = [' '.join(grocery_items[0:length_grocery])] #join first to x spot together to keep names
                groceries.append(grocery_items)
            elif len(grocery_items) < 3:
                groceries.append(grocery_items)
        if re.findall(r'\sx\s', grocery) and 'EUR' not in grocery: #find all the numbers of items bought and remove weighted products
            grocery_item = re.split (r'(\sx\s)', grocery)
            groceries.append(grocery_item)
    
    #find payment and date of purchase
    date_counter = 0 
    for grocery in raw_table_list:
        if re.findall(r'202[0-9]-[0-1][0-9]-[0-3][0-9]', grocery) and date_counter == 0:
            date = re.findall(r'202[0-9]-[0-1][0-9]-[0-3][0-9]', grocery)
            grocery = grocery.replace(grocery, date[0])
            groceries.append(['Date: ' + grocery])
            date_counter  = date_counter + 1 #only take the first date on the receipt
        elif re.findall(r'[0-3][0-9].+[0-1][0-9].+202[0-9]', grocery) and date_counter == 0:
            date = re.findall(r'[0-3][0-9].+[0-1][0-9].+202[0-9]', grocery)
            grocery = grocery.replace(grocery, date[0])
            groceries.append(['Date: ' + grocery])
            date_counter  = date_counter + 1 #only take the first date on the receipt
        if re.findall(r'(Bar\s[0-9]{1,2},[0-9]{2})|(Bezahlung)', grocery):
            groceries.append(['Payment: ' + grocery])
        
    """
    NOTE: COUPONS CANNOT BE READ BY ALGORITHM. It seems due to the color light blue?
    """
    return groceries

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
            if 'Date: ' in item:
                date_bought.append(item)
    date_bought = date_bought[0].lstrip('Date: ')
    
    grocery_name = []
    grocery_price = []
    grocery_count = []

    for grocery in grocery_list:
        if len(grocery) == 2:
            for index, item in enumerate(grocery):
                if index == 0:
                    grocery_name.append(item)
                if index == 1:
                    grocery_price.append(item)
            grocery_count.append(1)
        if len(grocery) == 3:
            grocery_count[-1] = grocery[0]
           
    data = {'grocery_name': grocery_name, 
            'grocery_price': grocery_price, 
            'grocery_count': grocery_count, 
            'payment_type': payment_type, 
            'date_of_purchase': date_bought,
            'store_bought_at': 'LIDL'}
    
    df = pd.DataFrame(data=data)
    return df

def clean_df(df):
    df['grocery_price'] = df['grocery_price'].str.replace('@', '0', regex = True) #@ symbol is often used instead of 0
    df['grocery_price'] = df['grocery_price'].str.replace('Q', '0', regex = True) #@ symbol is often used instead of Q
    df['grocery_price'] = df['grocery_price'].str.replace(',','.').astype('float')
    df['grocery_count'] = df['grocery_count'].astype('int')
    df['date_of_purchase'] = pd.to_datetime(df['date_of_purchase'], dayfirst=True).dt.strftime('%d.%m.%Y')
    df['weekday_purchased'] = pd.to_datetime(df['date_of_purchase'], dayfirst=True).dt.strftime('%A')

    """
    NOTE: Pfand seems to not be read correctly quiet a bit
    """
    return df


def check_final_price(cleaned_df):
    global COUNTING
    sum_price_user_input = LIDL_SUM[COUNTING]
    COUNTING = COUNTING + 1

    sum_price_df = round(cleaned_df['grocery_price'].sum(), 2)
    
    if len(LIDL_SUM) == 0:
        cleaned_df['check'] = 'not passed - no manual sum'
        return [cleaned_df, sum_price_df]
    
    elif sum_price_user_input == sum_price_df: #all good if both sums are same
        cleaned_df['check'] = 'passed'
        return [cleaned_df, sum_price_df]
    
    elif sum_price_user_input != sum_price_df: #problem if both sums are not the same
        missing_sum = sum_price_user_input - sum_price_df #find missing sum
        new_row = {'grocery_name': ['missing_input'], #add new row with missing input
            'grocery_price': [missing_sum], 
            'grocery_count': ['1'], 
            'payment_type': [cleaned_df.iloc[0,3]], 
            'date_of_purchase': [cleaned_df.iloc[0,4]],
            'store_bought_at': ['LIDL'],
            'weekday_purchased': [cleaned_df.iloc[0,6]]}
        new_df = pd.DataFrame(data=new_row) # create new dataframe with row
        cleaned_df = pd.concat([cleaned_df, new_df], ignore_index = True) #concat cleaned df with new df
        cleaned_df['check'] = 'not passed' #add column with not passed, as the sum did not match
        return [cleaned_df, sum_price_user_input]


def executer(original_bon):
    image_info = read_png_text(original_bon)
    lidl_bon = clean_lidl_bon(image_info)
    initial_df = create_df(lidl_bon)
    cleaned_df = clean_df(initial_df)
    final_df = check_final_price(cleaned_df)
    return final_df

