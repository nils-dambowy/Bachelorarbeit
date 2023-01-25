import pandas as pd
import mysql.connector


class Database_Connection():
    def __init__(self, mysql_connection):
        """
        mysql database connection to send queries using pandas

        mysql_connection format: mysql+mysqlconnector://USER@IP/DATABASE
            Replace USER,IP and DATABASE with your data.")
            For example: mysql+mysqlconnector://user:@127.0.0.1:3306/CNO
        """
        
        self.mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "0Skate1188!",
        database="thrakien_d4n4_2"
        )
        cursor = self.mydb.cursor(buffered=True)

        self.mysql_connection = mysql_connection
        self.cursor = self.mydb.cursor(buffered=True)

    def load_designs_from_db(self, table_name, column_list):
        """
        input:  table_name: Name of the mysql table
                column_list: A list containing all columns for the query, example: [ID, Name]

        return: pandas dataframe
        """
        select_query = ','.join(map(str, column_list))

        try:
            table = pd.read_sql_query("select " + select_query + " from " + table_name, self.mysql_connection)

        except:
             print("SQL query failed.")

        return table

    def load_design_with_id(self, table_name, coin_arr, column_list):
        """
        input:  table_name: Name of the mysql table
                column_list: A list containing all columns for the query, example: [ID, Name]

        return: pandas dataframe
        """
        select_query = ','.join(map(str, column_list))

        table_arr = []

        for coin_id in coin_arr:
            self.cursor.execute("select id_design from d2r_coin_obv_design where id_coin = '{}';".format(str(coin_id)))
            query_result = self.cursor.fetchall()
            design_id_obv = query_result[0][0]

            self.cursor.execute("select id_design from d2r_coin_rev_design where id_coin = '{}';".format(str(coin_id)))
            query_result = self.cursor.fetchall()
            design_id_rev = query_result[0][0]


            design_ids = [design_id_rev, design_id_obv]

            
            for id in design_ids:
                try:
                    table_arr.append(pd.read_sql_query("select " + select_query + " from " + table_name + " where id = '{}';".format(str(id)), self.mysql_connection))

                except:
                    print("SQL query failed.")

        return pd.concat(table_arr)


    def load_entities_from_db(self, table_name, column_list, columns_multi_entries=[], delimiter="", has_delimiter=False):
        """
        input:  table_name: Name of the mysql table
                column_list: A list containing all columns for the query, example: [ID, Name]
                columns_multi_entries: A list containing all columns having more than one element in a string, example "Alexander, Alexander the Great"
                delimiter, for example a comma
                has_delimiter: If there is a column with multi entries, set this parameter to true
        output: List containing all entities 
        """
        select_query = ','.join(map(str, column_list))

        try:
            table = pd.read_sql_query("select " + select_query + " from " + table_name, self.mysql_connection)

        except:
            print("SQL query failed.")


        columns_without_multi = list(set(column_list) - set(columns_multi_entries))

        exists = False
        values = []
        for column in columns_without_multi:
            if exists == False:
                values += table[column].tolist()
                exists = True
            else:
                values += table[column].tolist()
    
        if has_delimiter == True:
            for multi_column in columns_multi_entries:
                columns_with_multi = table[multi_column]
                multi_values = sum(columns_with_multi.fillna("").str.split(delimiter), [])
                values += multi_values

        return self.preprocess_entities(values)


    def preprocess_entities(self, entities):
        entities = [entity.strip() for entity in entities]
        entities = [entity for entity in entities if len(entity) > 0]
        capitalized_entities = [entity.capitalize() for entity in entities]
        entities += capitalized_entities
        return entities


    def create_own_query(self, query):
        try:
            return pd.read_sql_query(query, self.mysql_connection)

        except:
            print("SQL query failed.")













### This part must still be updated.
def replace_left_right_single_design(design):
    """
    preprocesses the data by replacing r. and l.

    Parameters
    -----------

    design: string
        the input sentence
    """
    a = design.strip()
    b = a.replace(" l.", " left")
    c = b.replace(" r.", " right")
    if not c.endswith("."):
        d = c + "."
    else:
        d = c
    return d

def replace_left_right_list_of_designs(designs):
    """
    Parameters
    ----------

    designs: list of strings
    """
    preprocessed_designs = []
    for design in designs:
        preprocessed_designs.append(replace_left_right_single_design(design))
    return preprocessed_designs

def replace_left_right(design):
    """
    Parameters
    ----------

    design: string or list of strings
    """
    if isinstance(design, str):
        return replace_left_right_single_design(design)
    elif isinstance(design, list):
        return replace_left_right_list_of_designs(design)
    elif isinstance(design, pd.DataFrame):
        res = design.copy()
        res["DesignEng"] = design["DesignEng"].map(replace_left_right_single_design)
        return res
    else:
        raise Exception("replace_left_right only accepts str of list of str as input")