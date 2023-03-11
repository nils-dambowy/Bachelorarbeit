from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace._XSD import XSD
import mysql.connector

prefix_dict = { 
                "meta"    : "http://www4.wiwiss.fu-berlin.de/bizer/d2r-server/metadata#", 
                "map"     : "#",
                "db"      : "<>",
                "rdf"     : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs"    : "http://www.w3.org/2000/01/rdf-schema#",
                "xsd"     : "http://www.w3.org/2001/XMLSchema#",
                "d2rq"    : "http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#",
                "d2r"     : "http://sites.wiwiss.fu-berlin.de/suhl/bizer/d2r-server/config.rdf#",
                "jdbc"    : "http://d2rq.org/terms/jdbc/",
                "skos"    : "http://www.w3.org/2004/02/skos/core#",
                "owl"     : "http://www.w3.org/2002/07/owl#",
                "foaf"    : "http://xmlns.com/foaf/0.1/",
                "un"      : "http://www.w3.org/2005/Incubator/urw3/XGR-urw3-20080331/Uncertainty.owl",
                "dcterms" : "http://purl.org/dc/terms/",
                "void"    : "http://rdfs.org/ns/void#/",
                "nm"      : "http://nomisma.org/id/",
                "nmo"     : "http://nomisma.org/ontology#",
                "cnt"     : "http://www.dbis.cs.uni-frankfurt.de/cnt/id/",
                "cn"      : "https://www.corpus-nummorum.eu/"
            }

def check_for_none(output, query):
    """
    Checks if the output for the used query 
    is None and if it is the case it prints
    the useq query for debugging.
    """
    if output is None:
        return "Error"
    else:
        return output

def map_coin(g, cursor, id, property_set, class_set):
    """
    Creates the rdf triples for with the overall information
    of the coin.

    Args:
        g            : the rdf graph
        cursor       : mysql cursor
        ids          : the ids of the coins
        property_set : _description_
        class_set    : _description_
    """

    ##########################
    # Coin general information
    ##########################
    cursor.execute("Select id from data_coins where id = {};".format(int(id)))
    query_result = cursor.fetchall()
    coin_id = check_for_none(query_result,"Select id from data_coins where id = {};.format(int(id))")
    pattern = "https://www.corpus-nummorum.eu/CN_"+ str(coin_id[0][0])

    #coin property bridges
    g.add((URIRef(pattern), URIRef(prefix_dict["nmo"]+"hasObjectType"), URIRef(prefix_dict["nm"]+"coin")))
    g.add((URIRef(pattern), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("coin_id="+str(id))))
    g.add((URIRef(pattern), URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["nmo"]+"NumismaticObject")))
    # Coin -> obverse_coin
    g.add((URIRef(pattern), URIRef(prefix_dict["nmo"]+"hasObverse"), URIRef("https://www.corpus-nummorum.eu/CN_{}#obverse".format(str(id)))))
    # Coin -> reverse_coin
    g.add((URIRef(pattern), URIRef(prefix_dict["nmo"]+"hasReverse"), URIRef("https://www.corpus-nummorum.eu/CN_{}#reverse".format(str(id)))))
    

    ###########################
    #  Designs --> ObverseCoins
    ###########################
    cursor.execute("Select id_design, design_en, design_de from d2r_coin_obv_design where id_coin = {};".format(int(id)))
    query_result = cursor.fetchall()
    myresult = check_for_none(query_result,"Select id_design, design_en, design_de from d2r_coin_obv_design where id_coin = {};.format(int(id))")

    # if coin has a obverse description:
    if myresult != []:
        #  Obverse --> DesignURI
        g.add( (URIRef("https://www.corpus-nummorum.eu/CN_{}#obverse".format(str(id))), URIRef(prefix_dict["nmo"]+"hasAppearance"), URIRef("https://www.corpus-nummorum.eu/designs/"+str(myresult[0][0]))))
        #  Obverse --> Design (en) 
        g.add( (URIRef("https://www.corpus-nummorum.eu/CN_{}#obverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]), lang="en")))
        #  Obverse --> Design (de) 
        g.add( (URIRef("https://www.corpus-nummorum.eu/CN_{}#obverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][2]), lang="de")))
    
    ###########################
    #  Designs --> ReverseCoins
    ###########################
    cursor.execute("Select id_design, design_en, design_de from d2r_coin_rev_design where id_coin = {};".format(int(id)))
    query_result = cursor.fetchall()
    myresult = check_for_none(query_result,"Select id_design, design_en, design_de from d2r_coin_rev_design where id_coin = {};.format(int(id))")

    # if coin has a reverse description:
    if myresult != []:
        # Reverse
        g.add( (URIRef("https://www.corpus-nummorum.eu/CN_{}#reverse".format(str(id))), URIRef(prefix_dict["nmo"]+"hasAppearance"), URIRef("https://www.corpus-nummorum.eu/designs/"+str(myresult[0][0]))))
        #  Obverse --> Design (en) Literal
        g.add( (URIRef("https://www.corpus-nummorum.eu/CN_{}#reverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]), lang="en")))
        #  Obverse --> Design (en) Literal
        g.add( (URIRef("https://www.corpus-nummorum.eu/CN_{}#reverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][2]), lang="de")))


        #######################
        # add property values
        #######################
        property_set.add(prefix_dict["nmo"]+"hasAppearance")
        property_set.add(prefix_dict["dcterms"]+"description")
        property_set.add(prefix_dict["nmo"]+"hasObjectType")
        property_set.add(prefix_dict["dcterms"]+"identifier")
        property_set.add(prefix_dict["rdf"]+"type")
        property_set.add(prefix_dict["nmo"]+"hasObverse")
        property_set.add(prefix_dict["nmo"]+"hasReverse")
        class_set.add(prefix_dict["nmo"]+"NumismaticObject")

def map_designs(g, cursor, id, property_set):
    """
    Maps the general information of the designs to rdf
    Args:
        g            : the rdf graph
        cursor       : mysql cursor
        ids          : the ids of the coins
        property_set : _description_
    """

    # retrieves the design id(reverse)
    cursor.execute("Select id_design from d2r_coin_rev_design where id_coin = {};".format(int(id)))
    query_result = cursor.fetchall() 
    if query_result == []:
        id_r = None
    else:
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_rev_design where id_coin = {};.format(int(id))") 
        id_r  = myresult[0][0]


    # retrieves the design id(obverse)
    cursor.execute("Select id_design from d2r_coin_obv_design where id_coin = {};".format(int(id)))
    query_result = cursor.fetchall()
    if query_result == []:
        #print("No Entry for Coin with ID: {} in d2r_coin_obv_design".format(id))
        id_o = None
    else:
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_obv_design where id_coin = {};.format(int(id))") 
        id_o  = myresult[0][0]

    if id_r != None:
        #######################
        # reverse design
        #######################
        # design id
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("design_id="+str(id_r))))
        #title
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"title"), Literal("CNT Design"+str(id_r))))
        #publisher
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"publisher"), Literal("Corpus Nummorum Thracorum")))
        
        # retrieves the descriptions of the design(de, en)
        cursor.execute("Select design_de, design_en from data_designs where id = {};".format(int(id_r)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result, "Select design_de, design_en from data_designs where id = {};.format(int(id_r))")

        # Design -> dcterms:descriptions (de)
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][0]), lang="de"))) 
        # Design -> dcterms:descriptions (en)
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]), lang="en")))

    if id_o != None:
        #######################
        # obverse design
        #######################
        # design id
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("design_id="+str(id_o))))
        #title
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"title"), Literal("CNT Design"+str(id_o))))
        #publisher
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"publisher"), Literal("Corpus Nummorum Thracorum")))
        
        # retrieves the descriptions of the design(de, en)
        cursor.execute("Select design_de, design_en from data_designs where id = {};".format(int(id_o)))
        query_result = cursor.fetchall() 
        myresult = check_for_none(query_result, "Select design_de, design_en from data_designs where id = {};.format(int(id_o))")

        # Design -> dcterms:descriptions (de)
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][0]), lang="de")))  
        # Design -> dcterms:descriptions (en)
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]), lang="en")))

    # add properties
    property_set.add(prefix_dict["dcterms"]+"identifier")
    property_set.add(prefix_dict["dcterms"]+"title")
    property_set.add(prefix_dict["dcterms"]+"publisher")

def map_reverse_nlp(g, cursor, cursor2, id, property_set, class_set):
    """
    Maps the NLP part of the reverse side
    Args:
        g : the rdf graph
        cursor (_type_): mysql cursor
        cursor2 (_type_): mysql cursor
        id (_type_): coin id
        property_set (_type_): _description_
        class_set (_type_): _description_
    """

    # retrieves the design id(reverse)
    cursor.execute("Select id_design from d2r_coin_rev_design where id_coin = {};".format(int(id)))
    query_result = cursor.fetchall() 

    if query_result == []:
        id_r = None
    else:
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_rev_design where id_coin = {};.format(int(id))") 
        id_r  = myresult[0][0]

    if id_r != None:
        ###############################
        # reverse
        ###############################

        # Designs --> nlp_bag (hasAppearance)
        design_bnode_bag_r_appr = BNode()
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_r)), URIRef(prefix_dict["nmo"]+"hasAppearance"), design_bnode_bag_r_appr))

        # Designs --> nlp_bag (hasIconography)
        design_bnode_bag_r_icon = BNode()
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_r)), URIRef(prefix_dict["nmo"]+"hasIconography"), design_bnode_bag_r_icon))
        
        # Design --> nlp_bag (blank node)
        # creating blank node for the bag of nlp words and labels over DesignID of cnt_pipeline_url_id table 
        g.add((design_bnode_bag_r_icon, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))
        g.add((design_bnode_bag_r_appr, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))


        ################################
        # Relationship Extraction
        ################################
        # select the entries of the design
        cursor.execute("Select id, subject_url, object_url, relation_url from cnt_pipeline_url where design_id = {};".format(int(id_r)))

        for res in cursor:
            # blank node for current entry
            curr_b_node = BNode()

            # assign entries the Statement class
            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Statement")))           


            #  nlp_bag --> entry
            g.add((design_bnode_bag_r_icon, URIRef(prefix_dict["rdf"]+"li"), curr_b_node))

            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"subject"), URIRef(res[1])))
            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"object"), URIRef(res[2])))
            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"predicate"), URIRef(res[3])))


        ################################
        # Named Entity Recognition
        ################################
        # select the named entities of the design
        cursor.execute("Select entity_url,entity,label_entity from cnt_pipeline_ner_url where design_id = {};".format(int(id_r))) 

        for res in cursor:
            # bag -> named entity
            g.add((design_bnode_bag_r_appr, URIRef(prefix_dict["rdf"]+"li"), URIRef(res[0])))
            g.add((URIRef(res[0]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(res[1], datatype=XSD.string)))
            
            # create labels
            try:
                cursor2.execute("select relation,relation_url, subject from cnt_pipeline_url where design_id = {};".format(int(id_r)))
                query_result = cursor2.fetchall()
                myres = check_for_none(query_result, "select relation,relation_url from cnt_pipeline_url, subject where design_id = {};.format(int(id_r))")

                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(myres[0][0], datatype=XSD.string)))
            except IndexError:
                # in case no relation was found in the description
                pass
            
            # create labels for predicates
            for resi in myres:
                cursor2.execute("select id from nlp_list_verb where name_en = '{}';".format(str(resi[0])))
                query_result = cursor2.fetchall()
                result = check_for_none(query_result, "select id from nlp_list_verb where name_en = '{}';.format(str(resi[0]))")
                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal("predicate_id="+str(result[0][0]))))
   
            # entity is a person
            if str(res[2]).lower() == "person":
                # retrieve id from the name or the alternativenames column
                try: 
                    cursor2.execute("select id from nlp_list_person where name   like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                    g.add((URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("subject_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II, Cat_III, Cat_IV, Cat_V from nlp_list_person where name like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

                except IndexError:
                    cursor2.execute("select id from nlp_list_person where alternativenames  like '%{}%';".format(str(res[1])))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")             
                    g.add((URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("subject_id="+str(result[0][0]))))
                    
                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II, Cat_III, Cat_IV, Cat_V from nlp_list_person where alternativenames  like '%{}%'".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))
            # entity is an animal                  
            elif str(res[2]).lower() == "animal":
                print("REVERSE ANIMAL: ", res)

                # retrieve id from the name or the alternativenames column
                try: 
                    cursor2.execute("select id from nlp_list_animal where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("object_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_animal where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

                except IndexError:
                    cursor2.execute("select id from nlp_list_animal where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("object_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_animal where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))
            
            # entity is an object
            elif str(res[2]).lower() == "object":
                # retrieve id from the name or the alternativenames column      
                try: 
                    cursor2.execute("select id from nlp_list_obj where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_obj where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II, Cat_III from nlp_list_obj where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))


                except IndexError:
                    cursor2.execute("select id from nlp_list_obj where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II, Cat_III from nlp_list_obj where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

            # entity is a plant
            else:
                # retrieve id from the name or the alternativenames column
                try: 
                    cursor2.execute("select id from nlp_list_plant where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_animal where name_en  like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))


                except IndexError:
                    cursor2.execute("select id from nlp_list_plant where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_animal where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

        # add propeties
        property_set.add(prefix_dict["nmo"]+"hasIconography")
        property_set.add(prefix_dict["nmo"]+"hasAppearance")
        property_set.add(prefix_dict["rdf"]+"type")
        property_set.add(prefix_dict["skos"]+"prefLabel")
        property_set.add(prefix_dict["rdf"]+"type")
        property_set.add(prefix_dict["rdf"]+"li")
        property_set.add(prefix_dict["rdf"]+"subject")
        property_set.add(prefix_dict["rdf"]+"object")
        property_set.add(prefix_dict["rdf"]+"predicate")
        class_set.add(prefix_dict["rdf"]+"Statement")
        class_set.add(prefix_dict["rdf"]+"Bag")

def map_obverse_nlp(g, cursor, cursor2, id):
    """_summary_

    Args:
        g       : the rdf graph
        cursor  : mysql cursor
        cursor2 : mysql cursor
        id      : id of coin
    """

    # retrieves the design id(obverse)
    cursor.execute("Select id_design from d2r_coin_obv_design where id_coin = {};".format(int(id)))
    query_result = cursor.fetchall()

    if query_result == []:
        id_o = None
    else:
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_obv_design where id_coin = {};.format(int(id))") 
        id_o  = myresult[0][0]

    if id_o != None:
        ###############################
        # obverse
        ###############################

        # Designs --> nlp_bag (hasAppearance)
        design_bnode_bag_o_appr = BNode()
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_o)), URIRef(prefix_dict["nmo"]+"hasAppearance"), design_bnode_bag_o_appr))

        # Designs --> nlp_bag (hasIconography)
        design_bnode_bag_o_icon = BNode()
        g.add((URIRef("https://data.corpus-nummorum.eu/api/designs/"+str(id_o)), URIRef(prefix_dict["nmo"]+"hasIconography"), design_bnode_bag_o_icon))
    

        # Design --> nlp_bag (blank node)
        # creating blank node for the bag of nlp words and labels over DesignID of cnt_pipeline_url_id table 
        g.add((design_bnode_bag_o_icon, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))
        g.add((design_bnode_bag_o_appr, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))

        ################################
        # Relationship Extraction
        ################################
        # select the entries of the design
        cursor.execute("Select id, subject_url, object_url, relation_url from cnt_pipeline_url where design_id = {};".format(int(id_o)))
        for res in cursor:
            # blank node for current entry
            curr_b_node = BNode()

            # assign entries the Statement class
            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Statement")))           

            #  nlp_bag --> entry
            g.add((design_bnode_bag_o_icon, URIRef(prefix_dict["rdf"]+"li"), curr_b_node))


            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"subject"), URIRef(res[1])))
            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"object"), URIRef(res[2])))
            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"predicate"), URIRef(res[3])))

        ################################
        # Named Entity Recognition
        ################################
        # select the named entities of the design

        cursor.execute("Select entity_url,entity,label_entity from cnt_pipeline_ner_url where design_id = {};".format(int(id_o))) 
        for res in cursor:
            # bag -> named entity
            g.add((design_bnode_bag_o_appr, URIRef(prefix_dict["rdf"]+"li"), URIRef(res[0])))
            g.add((URIRef(res[0]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(res[1], datatype=XSD.string)))

            # create labels
            try:
                cursor2.execute("select relation,relation_url from cnt_pipeline_url where design_id = {};".format(int(id_o)))
                query_result = cursor2.fetchall()
                myres = check_for_none(query_result, "select relation,relation_url from cnt_pipeline_url, subject where design_id = {};.format(int(id_r))")

                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(myres[0][0], datatype=XSD.string)))
            except IndexError:
                pass
            
            # create predicate labels
            for resi in myres:
                cursor2.execute("select id from nlp_list_verb where name_en = '{}';".format(str(resi[0])))
                query_result = cursor2.fetchall()
                result = check_for_none(query_result, "select id from nlp_list_verb where name_en = '{}';.format(str(resi[0]))")
                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal("predicate_id="+str(result[0][0]))))

            # entity is a person
            if str(res[2]).lower() == "person":
                # retrieve id from the name or the alternativenames column
                try: 
                    cursor2.execute("select id from nlp_list_person where name   like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                    g.add((URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("subject_id="+str(result[0][0]))))

                    # add cat I, cat II, cat III, cat IV and/or cat V
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II, Cat_III, Cat_IV, Cat_V from nlp_list_person where name like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")        
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

                except IndexError:
                    cursor2.execute("select id from nlp_list_person where alternativenames  like '%{}%';".format(str(res[1]).lower()))
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")              
                    g.add((URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("subject_id="+str(result[0][0]))))

                    # add cat I, cat II, cat III, cat IV and/or cat V
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II, Cat_III, Cat_IV, Cat_V from nlp_list_person where alternativenames like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                    
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")                  
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

            
            # entity is an animal
            elif str(res[2]).lower() == "animal":
                print("OBVERSE ANIMAL: ", res)
                # retrieve id from the name or the alternativenames column
                try: 
                    print("Try!")
                    cursor2.execute("select id from nlp_list_animal where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("object_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_animal where name like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    
                    print("ANI RESULTS: ", result)

                    for cat in result[0]:
                        print("ANI OBV CATs: ", cat)
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

                except IndexError:
                    print("Error!")
                    cursor2.execute("select id from nlp_list_animal where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("object_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_animal where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")   

                    print("ANI RESULTS: ", result)

                    for cat in result[0]:
                        print("ANI OBV CATs: ", cat)
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

            # entity is an object
            elif str(res[2]).lower() == "object":
                # retrieve id from the name or the alternativenames column   
                try: 
                    cursor2.execute("select id from nlp_list_obj where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_obj where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II, Cat_III from nlp_list_obj where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

                except IndexError:
                    cursor2.execute("select id from nlp_list_obj where alternativenames_en  like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_o)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_obj where alternativenames_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))
            
            # entity is a plant
            else:
                # retrieve id from the name or the alternativenames column       
                try: 
                    cursor2.execute("select id from nlp_list_plant where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_o)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_plant where name_en like '{}';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))


                except IndexError:
                    cursor2.execute("select id from nlp_list_plant where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_o)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                    # add cat I and/or cat II
                    # get the values of the categories
                    cursor2.execute("select Cat_I, Cat_II from nlp_list_obj where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")  
                    for cat in result[0]:
                        if cat is None:
                            # if category is empty
                            pass
                        else:
                            # search for category in nlp_hierarchy
                            # in order to retrieve the uri
                            # normal class uri
                            cursor2.execute("select class_uri from nlp_hierarchy where Class like '{}';".format(str(cat)))
                            query_result = cursor2.fetchall()
                            c_uri = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                            g.add((URIRef(res[0]), URIRef(prefix_dict["rdf"]+"type"), URIRef(c_uri[0][0])))

def create_hierachy(g, cursor, property_set, class_set):
    """_summary_

    Args:
        g (_type_): _description_
        cursor (_type_): _description_
        property_set (_type_): _description_
        class_set (_type_): _description_
    """
    cursor.execute("Select class, superclass, class_uri, superclass_uri from nlp_hierarchy;") 
    for (c,sc,cu,scu) in cursor:
        g.add((URIRef(cu), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(c, datatype=XSD.string)))
        g.add((URIRef(cu), URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdfs"]+"Class")))
        g.add((URIRef(cu), URIRef(prefix_dict["rdfs"]+"subClassOf"), URIRef(scu)))

    # add property and classes
    property_set.add(prefix_dict["rdfs"]+"subClassOf")
    class_set.add(prefix_dict["rdfs"]+"Class")

def create_prop_class(g, property_set, class_set):
    """_summary_

    Args:
        g (_type_): _description_
        property_set (_type_): _description_
        class_set (_type_): _description_
    """
    for prop in property_set:
        g.add((URIRef(prop), URIRef( prefix_dict["rdf"]+"type" ), URIRef(prefix_dict["rdf"]+"Property")))

    for c in class_set:
        g.add((URIRef(c), URIRef( prefix_dict["rdf"]+"type" ), URIRef(prefix_dict["rdfs"]+"Class")))

def serialize_graph(g):
    """_summary_

    Args:
        g (_type_): _description_
    """
    g.serialize(destination="output.nt", format="nt", encoding="utf-8")
    g.serialize(destination="tbl.ttl", format="ttl", encoding="utf-8")

def create_graph(ids):
    """_summary_

    Args:
        ids (_type_): _description_
    """
    
    g = Graph()

    # fill out with your own data
    mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "0Skate1188!",
    database="thrakien_d4n4_2"
    )
    cursor = mydb.cursor(buffered=True)

    # used for executing sql statements when iterating over the first cursor
    cursor2 = mydb.cursor(buffered=True) 

    # holds the different properties
    property_set = set()

    # holds the different classes
    class_set = set()

    if ids == "all":
        cursor.execute("Select id from data_coins;")
        query_result = cursor.fetchall()
        ids = [x[0] for x in query_result]

    for id in ids:
        map_coin(g, cursor, id, property_set, class_set)
        map_designs(g, cursor, id, property_set)
        map_reverse_nlp(g, cursor, cursor2, id, property_set, class_set)
        map_obverse_nlp(g, cursor, cursor2, id)

    create_hierachy(g, cursor, property_set, class_set)
    create_prop_class(g, property_set, class_set)
    serialize_graph(g)