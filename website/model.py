import pandas as pd
import psycopg2
import os

password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']
host = os.environ['DB_HOST']
name = os.environ['DB_NAME']
port = 5432

class DataModel(object):
    def __init__(self):
        self.conn = psycopg2.connect(dbname=name, host=host,
                                    password=password,user=user)
        self.cur = self.conn.cursor()
        self.categories = ['cleanser','serum','moisturizer']
        self.concerns = []
        self.product_list = []
        #self.df_columns = ['price','asin','imageurl','category','title','linkurl','confidence'] #columns from table. Will add the concerns when making select statement
        self.instruction_dictionary = {'moisturizer':'Moisturizers are the last product to be applied at night and applied before sunscreen during the day. \
                                                 They have different consistencies depending on which base ingredients were used (called emollients).\
                                                 Moisturizers are meant to sit on the surface of the skin as an added barrier against antioxidants, sun, and pollutants.',
                                  'serum':'Serums are applied one to two times per day after cleansing and toning. \
                                           Serums give you the most bang for your buck with active ingredients in smaller molecules meant to penetrate the skin.\
                                           Use a drop or two for the entire face and neck, rubbing in circles as it absorbs into the skin. \
                                           Using serums increases the strength of your beauty regimen and provide a more comprehensive \
                                           approach by including more than one serum in your routine.',
                                  'cleanser':'Cleansing is the first step in your beauty regimen. \
                                              Wash your face and neck in the morning and evening. \
                                              Cleansers are for washing dirt and makeup away.\
                                              It is important to pick good ingredients that are free of harsh chemicals and parabens.\
                                              Ingredients in cleansers do not penetrate the skin.',
                                  'peel/mask':'Masks and peels are applied to the skin once or twice a week. \
                                          They contain a high concentration of active ingredients dissolved in solvents and meant to penetrate the skin. \
                                          Masks and peels provide an added boost to your daily routine by leaving the ingredients on your skin for a longer period of time. \
                                          Like serums, you can use more than one during the week to round out your routine. \
                                          Apply after cleansing and toning and before serum and moisturizer,\
                                          leave on for 5-15 minutes before washing or peeling off (depending on the product). ',
                                  'toner':'Toners complete the cleansing of your skin by removing any impurities or oils that are still lingering after cleansing. \
                                           There are several types of toners that address different skin types: hydrating for dry skin, stringent for oily skin, and \
                                           calming for sensitive. They help balance the skin and increase absorption of ingredients in subsequent products. \
                                           After cleansing in the morning and evening, saturate two cotton pads and use on your face, neck, and decolletage.',
                                  'exfoliant':'Exfoliants brighten the skin, encourage new growth and prevent clogged pores by removing the top layer of dead cells. \
                                               Use natural ingredients that remove the skin gently, staying away from plastic microbeads (such as polyethylene), \
                                               harsh chemicals (such as DBP, BHA/BHT, and Triclosan), and silicones. Exfoliants can be used daily if gentle enough but \
                                               should be used at least once or twice a week. Apply after cleansing and toners and before masks/peels, serums, and treatments. \
                                               Use according the instructions, some exfoliants are left on while others are gently rubbed on skin and washed away with water.',
                                  'treatment':'Treatments are the heavy duty line of defense for addressing concerns. If you use serums and masks regularly but are looking for \
                                               something extra on a special occasion or for the occasional, transient concern, you can try a treatment. They have a higher \
                                               concentration of ingredients that can produce an immediate, temporary effect or to boost the effectiveness of your beauty regimen.\
                                               Use according to instructions once or twice a week.'}

        self.script_dictionary = {'moisturizer':'Important for all day defense against free radicals and environmental damage.', 
                                       'cleanser': 'A good cleanser is essential for removing dirt and pollutants from your skin.',
                                       'toner': 'Prep your skin with a hydrating toner to help subsequent products infuse better.',
                                       'exfoliant': 'Remove dead skin cells and dirt once or twice a week to give you an added glow.',
                                       'mask': 'The second line of defense for your skin concerns. Use with serum to see the biggest effect.',
                                       'peel': 'Refines your skin by removing the top epidermal layer.',
                                       'treatment': 'Use for an intense, targeted approach for specific concerns to round out your routine.',
                                       'serum': 'The most corrective for your biggest concerns.'
                                        }

    def import_data(self):
        query = '''
                SELECT m.*, p.price, p.title, p.imageurl, p.numberreviews, p.confidence
                FROM combined_aoc as m
                JOIN productinfo as p
                ON m.asin=p.asin
                '''

        self.df = pd.read_sql_query(query,self.conn)


    def _create_instruction_dictionary(self):
        get_instructions = '''SELECT *
                              FROM instructions'''
        self.cur.execute(get_instructions)
        rows = self.cur.fetchall()
        #print('rows of instructions = ',rows)
        for row in rows:
            self.instruction_dictionary[row[0]] = row[1].encode('utf-8')
       
    def get_recommendations(self,concerns):
        '''input: list of concerns
            return: product_list = list of product dictionaries
                             [
                                {concern1:product_total(double precision),
                                 concern2:product_total(double precision),
                                 etc,
                                 asin: text,
                                 title:text,
                                 imageurl:text,
                                 price:double precision,
                                 category:text,
                                 confidence: double precision}
                            ]
                             
                            '''
        self.concerns = concerns
        self.import_data()
        self.product_list.extend(self.df.to_dict(orient='records'))

        return(self.product_list)
