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
        print("Error with: {}!".format(str(query)))
        return "Error"
    else:
        return output

def create_coin_map(g, cursor, ids, property_set, class_set):
    for id in ids:
        print("Working on ID: ", id)
        cursor.execute("Select id from data_coins where id = {};".format(int(id)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result,"Select id from data_coins where id = {};.format(int(id))")

        pattern = "https://www.corpus-nummorum.eu/coins/"+ str(myresult[0][0])

        #coin property bridges
        g.add((URIRef(pattern), URIRef(prefix_dict["nmo"]+"hasObjectType"), URIRef(prefix_dict["nm"]+"coin")))
        g.add((URIRef(pattern), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("coin_id="+str(id))))
        g.add((URIRef(pattern), URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["nmo"]+"NumismaticObject")))

        # Coin -> obverse_coin
        # Coin -> reverse_coin
        g.add((URIRef(pattern), URIRef(prefix_dict["nmo"]+"hasObverse"), URIRef("https://www.corpus-nummorum.eu/coins?id={}#obverse".format(str(id)))))
        g.add((URIRef(pattern), URIRef(prefix_dict["nmo"]+"hasReverse"), URIRef("https://www.corpus-nummorum.eu/coins?id={}#reverse".format(str(id)))))

        #  Designs --> ObverseCoins
        cursor.execute("Select id_design, design_en, design_de from d2r_coin_obv_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result,"Select id_design, design_en, design_de from d2r_coin_obv_design where id_coin = {};.format(int(id))")

        g.add( (URIRef("https://www.corpus-nummorum.eu/coins?id={}#obverse".format(str(id))), URIRef(prefix_dict["nmo"]+"hasAppearance"), URIRef("https://www.corpus-nummorum.eu/designs/"+str(myresult[0][0]))))
        #  Obverse --> Design (en) Literal
        g.add( (URIRef("https://www.corpus-nummorum.eu/coins?id={}#obverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]))))
        #  Obverse --> Design (en) Literal
        g.add( (URIRef("https://www.corpus-nummorum.eu/coins?id={}#obverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][2]))))

        #  Designs --> ReverseCoins
        cursor.execute("Select id_design, design_en, design_de from d2r_coin_rev_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result,"Select id_design, design_en, design_de from d2r_coin_rev_design where id_coin = {};.format(int(id))")

        g.add( (URIRef("https://www.corpus-nummorum.eu/coins?id={}#reverse".format(str(id))), URIRef(prefix_dict["nmo"]+"hasAppearance"), URIRef("https://www.corpus-nummorum.eu/designs/"+str(myresult[0][0]))))
        #  Obverse --> Design (en) Literal
        g.add( (URIRef("https://www.corpus-nummorum.eu/coins?id={}#reverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]))))
        #  Obverse --> Design (en) Literal
        g.add( (URIRef("https://www.corpus-nummorum.eu/coins?id={}#reverse".format(str(id))), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][2]))))



        # add property values
        property_set.add(prefix_dict["nmo"]+"hasAppearance")
        property_set.add(prefix_dict["dcterms"]+"description")


        #add property values
        property_set.add(prefix_dict["nmo"]+"hasObjectType")
        property_set.add(prefix_dict["dcterms"]+"identifier")
        property_set.add(prefix_dict["rdf"]+"type")
        property_set.add(prefix_dict["nmo"]+"hasObverse")
        property_set.add(prefix_dict["nmo"]+"hasReverse")
        class_set.add(prefix_dict["nmo"]+"NumismaticObject")

def create_design_triples(g, cursor, ids, property_set):
    for id in ids:
        print("Working on ID: ", id)
        cursor.execute("Select id_design from d2r_coin_rev_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall() 
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_rev_design where id_coin = {};.format(int(id))") 

        id_r  = myresult[0][0]

        cursor.execute("Select id_design from d2r_coin_obv_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_obv_design where id_coin = {};.format(int(id))") 

        id_o  = myresult[0][0]



        #reverse
        # design identifier
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("design_id="+str(id_r))))
        #title
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"title"), Literal("CNT Design"+str(id_r))))
        #publisher
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"publisher"), Literal("Corpus Nummorum Thracorum")))
        
        # Designs --> Iconography 
        cursor.execute("Select design_de, design_en from data_designs where id = {};".format(int(id_r)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result, "Select design_de, design_en from data_designs where id = {};.format(int(id_r))")

        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][0])))) 
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_r)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]))))



        #obverse
        # design identifier
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("design_id="+str(id_o))))
        #title
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"title"), Literal("CNT Design"+str(id_o))))
        #publisher
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"publisher"), Literal("Corpus Nummorum Thracorum")))
        
        # Designs --> Iconography 
        cursor.execute("Select design_de, design_en from data_designs where id = {};".format(int(id_o)))
        query_result = cursor.fetchall() 
        myresult = check_for_none(query_result, "Select design_de, design_en from data_designs where id = {};.format(int(id_o))")

        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][0]))))  
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_o)), URIRef(prefix_dict["dcterms"]+"description"), Literal(str(myresult[0][1]))))

    # add properties
    property_set.add(prefix_dict["dcterms"]+"identifier")
    property_set.add(prefix_dict["dcterms"]+"title")
    property_set.add(prefix_dict["dcterms"]+"publisher")

def create_reverse(g, cursor, cursor2, ids, property_set, class_set):
    for id in ids:
    
        print("Working on ID: ", id)
        cursor.execute("Select id_design from d2r_coin_rev_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall() 
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_rev_design where id_coin = {};.format(int(id))") 

        id_r  = myresult[0][0]

        cursor.execute("Select id_design from d2r_coin_obv_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_obv_design where id_coin = {};.format(int(id))") 

        id_o  = myresult[0][0]
        
        #reverse
        #  Designs --> nlp_bag
        design_bnode_bag_r_appr = BNode()
        design_bnode_bag_r_icon = BNode()
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_r)), URIRef(prefix_dict["nmo"]+"hasIconography"), design_bnode_bag_r_icon))
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_r)), URIRef(prefix_dict["nmo"]+"hasAppearance"), design_bnode_bag_r_appr))

        #  Design --> nlp_bag (blank node)
        # creating blank node for the bag of nlp words and labels over DesignID of cnt_pipeline_url_id table 
        g.add((design_bnode_bag_r_icon, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))
        g.add((design_bnode_bag_r_appr, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))

        #  Design --> nlp_entries (blank node)
        ######################
        # creating a blank node for the entries of the nlp_bag
        nodes_rev = []
        cursor.execute("Select id from cnt_pipeline_url where design_id = {};".format(int(id_r)))

        for res in cursor:
            curr_b_node = BNode()
            nodes_rev.append(curr_b_node)

            cursor2.execute("select relation,relation_url from cnt_pipeline_url where design_id = {};".format(int(id_r)))
            query_result = cursor2.fetchall()
            myres = check_for_none(query_result, "select relation,relation_url from cnt_pipeline_url where design_id = {};.format(int(id_r))")

            g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(myres[0][0], datatype=XSD.string)))

            #has Iconography Part

            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Statement")))
            #  nlp_bag --> Parts
            g.add((design_bnode_bag_r_icon, URIRef(prefix_dict["rdf"]+"li"), curr_b_node))

            ######################
            #  nlp_entry --> person as subject
            ######################
            cursor2.execute("Select subject_url, object_url, relation_url from cnt_pipeline_url where design_id = {};".format(int(id_r)))
            query_result = cursor2.fetchall()
            myresult = check_for_none(query_result, "Select subject_url, object_url, relation_url from cnt_pipeline_url where design_id = {};.format(int(id_r))")

            for i in range(len(myresult)):
                g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"subject"), URIRef(myresult[i][0])))
                g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"object"), URIRef(myresult[i][1])))
                g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"predicate"), URIRef(myresult[i][2])))


        cursor.execute("Select entity_url,entity,label_entity from cnt_pipeline_ner_url where design_id = {};".format(int(id_r))) 

        for res in cursor:
            g.add((design_bnode_bag_r_appr, URIRef(prefix_dict["rdf"]+"li"), URIRef(res[0])))
            g.add((URIRef(res[0]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(res[1], datatype=XSD.string)))
            
            try:
                cursor2.execute("select relation,relation_url, subject from cnt_pipeline_url where design_id = {};".format(int(id_r)))
                query_result = cursor2.fetchall()
                myres = check_for_none(query_result, "select relation,relation_url from cnt_pipeline_url, subject where design_id = {};.format(int(id_r))")

                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(myres[0][0], datatype=XSD.string)))
            except IndexError:
                print("No Relation. See Design {}.".format(str(id_r)))
        
            for resi in myres:
                cursor2.execute("select id from nlp_list_verb where name_en = '{}';".format(str(resi[0])))
                query_result = cursor2.fetchall()
                result = check_for_none(query_result, "select id from nlp_list_verb where name_en = '{}';.format(str(resi[0]))")
                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal("predicate_id="+str(result[0][0]))))

            if str(res[2]).lower() == "person":
                # person
                try: 
                    cursor2.execute("select id from nlp_list_person where name   like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")
                    g.add((URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("subject_id="+str(result[0][0]))))

                except IndexError:
                    cursor2.execute("select id from nlp_list_person where alternativenames  like '%{}%';".format(str(res[1]).lower()))
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")              
                    g.add((URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("subject_id="+str(result[0][0]))))
                
                
            elif str(res[2]).lower() == "animal":
                # animal
                try: 
                    cursor2.execute("select id from nlp_list_animal where name_en like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                except IndexError:
                    cursor2.execute("select id from nlp_list_animal where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

            elif str(res[2]).lower() == "object":
                # objects        
                try: 
                    cursor2.execute("select id from nlp_list_obj where name_en like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_obj where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                except IndexError:
                    cursor2.execute("select id from nlp_list_obj where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))


            else:
                # plants
                try: 
                    cursor2.execute("select id from nlp_list_plant where name_en like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                except IndexError:
                    cursor2.execute("select id from nlp_list_plant where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

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

def create_obverse(g, cursor, cursor2, ids):
    for id in ids:
        
        print("Working on ID: ", id)
        cursor.execute("Select id_design from d2r_coin_rev_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall() 
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_rev_design where id_coin = {};.format(int(id))") 

        id_r  = myresult[0][0]

        cursor.execute("Select id_design from d2r_coin_obv_design where id_coin = {};".format(int(id)))
        query_result = cursor.fetchall()
        myresult = check_for_none(query_result, "Select id_design from d2r_coin_obv_design where id_coin = {};.format(int(id))") 

        id_o  = myresult[0][0]
        
        #reverse
        #  Designs --> nlp_bag
        design_bnode_bag_o_appr = BNode()
        design_bnode_bag_o_icon = BNode()
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_o)), URIRef(prefix_dict["nmo"]+"hasIconography"), design_bnode_bag_o_icon))
        g.add((URIRef("https://www.corpus-nummorum.eu/designs/"+str(id_o)), URIRef(prefix_dict["nmo"]+"hasAppearance"), design_bnode_bag_o_appr))

        #  Design --> nlp_bag (blank node)
        # creating blank node for the bag of nlp words and labels over DesignID of cnt_pipeline_url_id table 
        g.add((design_bnode_bag_o_icon, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))
        g.add((design_bnode_bag_o_appr, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Bag")))

        #  Design --> nlp_entries (blank node)
        ######################
        # creating a blank node for the entries of the nlp_bag
        nodes_rev = []
        cursor.execute("Select id from cnt_pipeline_url where design_id = {};".format(int(id_o)))

        for res in cursor:
            curr_b_node = BNode()
            nodes_rev.append(curr_b_node)

            cursor2.execute("select relation,relation_url from cnt_pipeline_url where design_id = {};".format(int(id_o)))
            query_result = cursor2.fetchall()
            myres = check_for_none(query_result, "select relation,relation_url from cnt_pipeline_url where design_id = {};.format(int(id_r))")

            g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(myres[0][0], datatype=XSD.string)))

            #has Iconography Part

            g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdf"]+"Statement")))
            #  nlp_bag --> Parts
            g.add((design_bnode_bag_o_icon, URIRef(prefix_dict["rdf"]+"li"), curr_b_node))

            ######################
            #  nlp_entry --> person as subject
            ######################
            cursor2.execute("Select subject_url, object_url, relation_url from cnt_pipeline_url where design_id = {};".format(int(id_o)))
            query_result = cursor2.fetchall()
            myresult = check_for_none(query_result, "Select subject_url, object_url, relation_url from cnt_pipeline_url where design_id = {};.format(int(id_r))")

            for i in range(len(myresult)):
                g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"subject"), URIRef(myresult[i][0])))
                g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"object"), URIRef(myresult[i][1])))
                g.add((curr_b_node, URIRef(prefix_dict["rdf"]+"predicate"), URIRef(myresult[i][2])))


        cursor.execute("Select entity_url,entity,label_entity from cnt_pipeline_ner_url where design_id = {};".format(int(id_o))) 

        for res in cursor:

            g.add((design_bnode_bag_o_appr, URIRef(prefix_dict["rdf"]+"li"), URIRef(res[0])))
            g.add((URIRef(res[0]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(res[1], datatype=XSD.string)))
            
            try:
                cursor2.execute("select relation,relation_url, subject from cnt_pipeline_url where design_id = {};".format(int(id_o)))
                query_result = cursor2.fetchall()
                myres = check_for_none(query_result, "select relation,relation_url from cnt_pipeline_url, subject where design_id = {};.format(int(id_r))")

                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(myres[0][0], datatype=XSD.string)))
            except IndexError:
                print("No Relation. See Design {}".format(str(id_o)))
        
            for resi in myres:
                cursor2.execute("select id from nlp_list_verb where name_en = '{}';".format(str(resi[0])))
                query_result = cursor2.fetchall()
                result = check_for_none(query_result, "select id from nlp_list_verb where name_en = '{}';.format(str(resi[0]))")
                g.add((URIRef(myres[0][1]), URIRef(prefix_dict["skos"]+"prefLabel"), Literal("predicate_id="+str(result[0][0]))))

            if str(res[2]).lower() == "person":
                # person
                try: 
                    cursor2.execute("select id from nlp_list_person where name   like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")

                except IndexError:
                    cursor2.execute("select id from nlp_list_person where alternativenames  like '%{}%';".format(str(res[1]).lower()))
                    result = check_for_none(query_result, "select id from nlp_list_person where name = {} or where alternativenames;.format(id_r)")              

                g.add((URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal("subject_id="+str(result[0][0]))))
                
            elif str(res[2]).lower() == "animal":
                # animal
                try: 
                    cursor2.execute("select id from nlp_list_animal where name_en like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                except IndexError:
                    cursor2.execute("select id from nlp_list_animal where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_animal where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

            elif str(res[2]).lower() == "object":
                # objects        
                try: 
                    cursor2.execute("select id from nlp_list_obj where name_en like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_obj where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                except IndexError:
                    cursor2.execute("select id from nlp_list_obj where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))
            
            else:
                # plants
                try: 
                    cursor2.execute("select id from nlp_list_plant where name_en like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

                except IndexError:
                    cursor2.execute("select id from nlp_list_plant where alternativenames_en  like '%{}%';".format(str(res[1]).lower()))
                    query_result = cursor2.fetchall()
                    result = check_for_none(query_result, "select id from nlp_list_plant where name = {} or where alternativenames;.format(id_r)")  
                    g.add( (URIRef(res[0]), URIRef(prefix_dict["dcterms"]+"identifier"), Literal(str(res[2]).lower()+"_id="+str(result[0][0]))))

def create_hierachy(g, cursor, property_set, class_set):
    cursor.execute("Select class, superclass, class_uri, superclass_uri from nlp_hierarchy;") 
    for (c,sc,cu,scu) in cursor:
        g.add((URIRef(cu), URIRef(prefix_dict["skos"]+"prefLabel"), Literal(c, datatype=XSD.string)))
        g.add((URIRef(cu), URIRef(prefix_dict["rdf"]+"type"), URIRef(prefix_dict["rdfs"]+"Class")))
        g.add((URIRef(cu), URIRef(prefix_dict["rdfs"]+"subClassOf"), URIRef(scu)))

    # add property
    property_set.add(prefix_dict["rdfs"]+"subClassOf")
    class_set.add(prefix_dict["rdfs"]+"Class")

def create_prop_class(g, property_set, class_set):
    for prop in property_set:
        g.add((URIRef(prop), URIRef( prefix_dict["rdf"]+"type" ), URIRef(prefix_dict["rdf"]+"Property")))

    for c in class_set:
        g.add((URIRef(c), URIRef( prefix_dict["rdfs"]+"Class" ), URIRef(prefix_dict["rdf"]+"Class")))

def serialize_graph(g):
    g.serialize(destination="output.nt", format="nt", encoding="utf-8")
    g.serialize(destination="tbl.ttl", format="ttl", encoding="utf-8")

def create_graph(ids):

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

    create_coin_map(g, cursor, ids, property_set, class_set)
    create_design_triples(g, cursor, ids, property_set)
    create_reverse(g, cursor, cursor2, ids, property_set, class_set)
    create_obverse(g, cursor, cursor2, ids)
    create_hierachy(g, cursor, property_set, class_set)
    create_prop_class(g, property_set, class_set)
    serialize_graph(g)
