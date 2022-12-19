'''The goal of thiss assignment is to grab info from the
SQL rpg database and transfer data through a pipeline to
a new document oriented/non relational mongo database.'''

import pymongo
import sqlite3

PASSWORD = '1TKUHyWgpIxF0J0g'
DBNAME = 'rpg_data'

def create_mdb_connection(password, dbname):
    '''create connection to mongodb database'''
    client = pymongo.MongoClient(f'mongodb+srv://charlieblk9400:{password}@cluster0.tszlrua.mongodb.net/{dbname}?retryWrites=true&w=majority')
    return client

def create_sl_connection(dbname='rpg_db.sqlite3'):
    '''create the connection to the rpg sqlite database'''
    sl_conn = sqlite3.connect(dbname)
    return sl_conn

def execute_query(curs, query):
    '''enable us to get data OUT of the sqlite database'''
    return curs.execute(query).fetchall()

def doc_creation(db, sl_curs, character_table_query, item_table_query, weapon_table_query):
    '''creates the documents that will live in our rpg_data collection
     by using our queries and the sqlite connection to grab the data
    from the sqlite3 database'''
    weapons = execute_query(sl_curs, weapon_table_query)
    characters = execute_query(sl_curs, character_table_query)
    for character in characters:
        item_character_query = item_table_query.format("\'%s\'" % character[1])
        item_names = execute_query(sl_curs, item_character_query)
        # %s is use specifically when we are inserting some item from a tuple
        #calling item_table _query and putting in it a character name in quotation marks
        weapon_names = []
        for item in item_names:
            if item in weapons:
                weapon_names.append(item[0])

        document = {
            'name': character[1],
            'level': character[2],
            'exp': character[3],
            'hp': character[4],
            'strength': character[5],
            'intelligence': character[6],
            'dexterity': character[7],
            'wisdom': character[8],
            'items': item_names,
            'weapons': weapon_names
        }

        db.insert_one(document)



def show_all(db):
    '''we will look inside the database collection rpg_data by passing
    in db. we will get all the documents in the database and put them
    in a list'''
    all_docs = list(db.find())
    return all_docs


GET_CHARACTER_TABLE = '''
    SELECT * FROM charactercreator_character
    '''

GET_ITEM_TABLE = '''
    SELECT ai.name AS item_name
    FROM (SELECT * 
    FROM charactercreator_character AS cc_char
    INNER JOIN charactercreator_character_inventory AS cc_inv
    WHERE cc_char.character_id = cc_inv.character_id) AS char_ci
    INNER JOIN armory_item AS ai
    WHERE ai.item_id = char_ci.item_id
    AND char_ci.name = {};
    '''

#get me the names of items that are weapons inside characters inventories
GET_WEAPON_TABLE = '''
    SELECT  aw_ai.name
    FROM  (SELECT * 
    FROM armory_item AS ai
    INNER JOIN armory_weapon AS aw
    ON ai.item_id = aw.item_ptr_id) AS aw_ai
    INNER JOIN (SELECT * 
    FROM charactercreator_character AS cc_char
    INNER JOIN charactercreator_character_inventory AS cc_inv
    WHERE cc_char.character_id = cc_inv.character_id) AS char_ci
    WHERE aw_ai.item_id = char_ci.item_id;
    '''

if __name__ == '__main__':
    sl_conn = create_sl_connection()
    sl_curs = sl_conn.cursor()
    client = create_mdb_connection(PASSWORD, DBNAME)
    # print(client)
    
    #connect to the collection that we want to add documents to 
    #before we insert data to mongo db we must to to the site and create the database and collection
    
    db = client.rpg_data.rpg_data
    
    # #drop anything that is already in the collection
    
  
    doc_creation(db, sl_curs, GET_CHARACTER_TABLE, GET_ITEM_TABLE, GET_WEAPON_TABLE)

    print(show_all(db))
