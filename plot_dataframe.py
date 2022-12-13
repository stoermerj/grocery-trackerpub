import plotly.express as px
import pandas as pd
from datetime import datetime


#used for testing purposes
#df = pd.read_csv('einkaufszettel1_with_categories.csv')
#df = df.set_index('Unnamed: 0')

#function is used to provide user with undefined elements that need to be categorized
def check_for_undefined_categories(df):
       df_undefined = df[df['food_categories'] == 'undefined']
       if len(df_undefined.index) == 0:
              print('Great Job, all grocery elements are categorized')
              return 0
       else:
              print(df_undefined)
              return df_undefined

def download_files(df):
       today = datetime.now().date()
       file_name = str(today)+'_bon_data'+'.csv'
       df.to_csv(file_name)

def show_plots(df):
       #understand what type of food category is bought the most from a store
       most_bought_food_category = df.groupby(['food_categories', 'store_bought_at'], as_index=False)['grocery_count'].sum()
       fig = px.bar(most_bought_food_category, x = 'food_categories', y= 'grocery_count', color = 'store_bought_at')
       fig.show()

       #understand the price for each food category
       highest_price_food_category = df.groupby(['food_categories', 'store_bought_at'], as_index=False)['grocery_price'].sum()
       fig2 = px.bar(highest_price_food_category, x = 'food_categories', y = 'grocery_price', color = 'store_bought_at')
       fig2.show()

       highest_price_grocery_store = df.groupby(['store_bought_at'], as_index=False)['grocery_price'].sum()
       fig3 = px.bar(highest_price_grocery_store, x = 'store_bought_at', y = 'grocery_price')
       fig3.show()

       #understand what weekday was used for grocery shopping
       weekday_used_for_purchase = df.groupby(['store_bought_at', 'weekday_purchased'], as_index = False)['grocery_price'].sum()
       fig4 = px.bar(weekday_used_for_purchase, x = 'weekday_purchased', y = 'grocery_price')
       fig4.show()