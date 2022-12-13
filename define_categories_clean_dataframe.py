import pandas as pd
import numpy as np

#used for testing purposes
#df = pd.read_csv('einkaufszettel.csv')
#df = df.set_index('Unnamed: 0')

def categorizer(df):
    categories = {'suesses_knabbereien' : ['Mentos', 'KARAMEL SUTRA', 'ESZET VOLLMILCH', 'GELEE ERDBEER HI', 'WILLIS ROTE FR.', 'Apfelmus'],
                  'fleisch_wurst' : ['BIO RINDERHACK', 'Salami', 'BIO HACK SW RD', 'KOCHSCHINKEN', 'PUTE'],
                  'fisch_meeresfruechte' : ['Thunf', 'Lachsspitzen', 'HERINGSFILET', 'MUSCHELN', 'Frutti di Mare', ],
                  'obst_gemuese_salate' : ['Blumenkohl', 'Romatomaten', 'Paprika', 'Zucchini', 'Zwiebeln', 'Sukkartofel', 'Birne', 'Banane', 'Limette', 'Avocado', 'Mohren',
                           'Dattelcherrytomaten', 'Gurke', 'Mango', 'Trauben', 'Champignon', 'Knoblauch', 'Apfel', 'Datteln', 'Cherrystrauchtomaten', 
                           'Bio Cocktailstaucht','Cranberries', 'Wassermelone', 'KAROTTE', 'KUERBIS', 'ROMARISPENTOM.', 'CHAMP. WEISS', 'MELONE HONIG',
                           'INGWER', 'SUESSKARTOFFEL', 'RISPENTOMATE', 'GRUENE OLIVEN', 'BROCCOLI', 'PFIRSICHE', 'Sukkartoffel kg', 'KARTOFFELGEM.', 'Bioland Speisekart.',
                           'Porree', 'Oliven', 'Knollensell'],
                  'milchprodukte_eier' : ['Joghurt', 'Kerrygold gesalzen', 'Sauerrahm', 'Eier', 'Valensina', 'Jogh', 'Emmentaler', 'Milch', 'Rama', 'Butter', 'Frischkase',
                          'Cremosano', 'Halloumi Grillkase', 'FRUCHTJOGH', 'ALMIGHURT', 'KAESEAUFSCHNITT', 'ALMZEIT ALPENK.', 'Bergkase', 'FRISCHKAESE',
                          'EXQUISA JOGHURT', 'NATURJOGH.1,5%', 'EXQUISA SAHNIGE', 'QUARK', 'Gouda Scheiben', 'Rama', 'Fraiche', 'Hirtenkase'],
                  'konserven_pasta' : ['Tomatenmark', 'Bio Gemisebritthhe Glas', 'Suppengrtn', 'Gehackte Tomaten', 'TAGLIAT.+SPINAT', 'TORTIGLIONI', 'Zucker',
                                       'KICHERERBSEN', 'W.RIESENBOHNEN', 'BRECHBOHNEN', 'Fusilli', 'Gnocchi', 'Penne Rigate', 'WeiRe Riesenbohnen'],
                  'fertiggerichte' : [],
                  'brot_muesli' : ['Wraps', 'FLADENBROT', 'HAFERFLOCK', 'ZWIEBACK'],
                  'brotaufstriche_belag' : ['Senf', ],
                  'gewuerze_oele_fette' : ['Pfeffer', 'Majoran', 'Hefe', 'Curry', 'Balsamico', 'ALPENJODSALZ', 'Klas Oil Sonnenbl.01', 'Bio Olivenél extra'],
                  'getraenke_gut' : ['Hohes C', 'Mineralwasser', 'Dallmayr', 'Valensina','PRODOMO', 'FENCHEL ANIS'],
                  'getraenke_schlecht' : ['Coca Cola', 'Schwipp Schwap', 'Zero', 'Ice Tea', 'Lipton', 'Pepsi', 'GIESINGER', 'WEISSER PFIRSICH', 'PINK GRAPEFRUIT', 'LIPTON ZITRONE', 
                          'FRITZ KOLA', 'Red Bull'],
                  'pfand_rabatt' : ['Pfand', 'LEERG'],
                  'missing_input' : ['missing_input'],
                  'baby' : ['baby', 'dmBio', 'Hipp', 'Schmelzfl', 'Bebivita', 'Avent', 'Wollsöckchen', 'Mivolis', 'Weichweizen', 'BIRNE MIT APFEL', 'GEMUESE RIND', 
                            'RIGATONI NAPOLI', 'GEMUESE LASAGNE', 'FR.-FREUND ZEBRA', 'BAN.,ERDB.,QUIN.', 'APFEL ERDB.FEIGE', 'KOLA SUPERZERO', 'APF.BAN.MUESLIE', 
                            'RIGATONI NAPOLI', 'SPAGHETTI BOL', 'Maisstangen', 'FEUCHTTUECHER'],
                  'haushaltswaren' : ['Odol-med', 'elmex', 'Schwammtücher', 'Spezialsalz', 'Handschuhe', 'Shampoo', 'Persil', 'Finish', 'Ariel', 'Toilettenpapier',
                                      ]
    }

    df['food_categories'] = 'undefined'

    for category, food_labels in categories.items():
        for food_label in food_labels:
            contains_food_label = df.loc[df['grocery_name'].str.contains(food_label, case=False)]
            contains_food_label = contains_food_label.index
            for index in contains_food_label:
                df.at[index, 'food_categories'] = category
    return df

def clean_dataframe(df):
    #repeat the rows n times with n amount of gocery_count
    df['grocery_count'] = df['grocery_count'].astype('int')
    df['grocery_price'] = np.where(df['grocery_count'] > 1, df['grocery_price']/df['grocery_count'], df['grocery_price'])
    
    df = df.loc[df.index.repeat(df.grocery_count)]
    df = df.reset_index()
    df = df.drop(['index', 'grocery_count'], axis = 1)
    #df = df.drop(['Unnamed: 0', 'grocery_count'], axis = 1) #only use for testing pruposes
    df['grocery_count'] = 1
    
    #clean payment_type
    df['payment_type'].loc[df['payment_type'].str.contains('Visa', case = False)] = 'Visa'
    
    #change dtype of columns
    df['date_of_purchase'] = pd.to_datetime(df['date_of_purchase'], infer_datetime_format=True)
    df['store_bought_at'] = df['store_bought_at'].astype('category')
    df['food_categories'] = df['food_categories'].astype('category')
    df['grocery_count'] = df['grocery_count'].astype('int')
    return df

def executer(df):
    dataframe = categorizer(df)
    dataframe = clean_dataframe(dataframe)
    return dataframe

#executer(df)
