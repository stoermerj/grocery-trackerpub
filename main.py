import combine_dataframes
import define_categories_clean_dataframe
import plot_dataframe

def main():
    df = combine_dataframes.combine_files(combine_dataframes.PATHS)
    df = define_categories_clean_dataframe.executer(df)
    print(df)
    plot_dataframe.check_for_undefined_categories(df)
    plot_dataframe.download_files(df)
    plot_dataframe.show_plots(df)
    
if __name__ == '__main__':
  main()