# grocery-trackerpub

This application helps track and analyze your grocery spendings from the retailers rewe and lidl by:

    - providing a list of spendings with multiple features as colums in a .csv file
    - providing an initial analysis with plots

The following steps have to be undertaken before analysis:

    - update LIDL_SUM in lidl_extract_bon_data.py with total cost of each bon. Has to be done as LIDL only provides a png that sometimes limits the accuracy of data
    - upload the bons in either DM, LIDL or Rewe folder. Other grocery stores have not been added as these are not used or do not provide a digital bon
    - update any undefined categories that have not been defined yet in define_categories_clean_dataframe.py
    - run program
    - should any undefined categories come up, it will print them in the terminal. You can define these again in the above python file
    - once the program successfully runs, a csv is printed and four graphs will show it in the browser.
    - interpret
