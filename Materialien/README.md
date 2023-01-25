# NLP-on-multilingual-coin-descriptions

Accessing relevant information from Corpus Numorum Online iconographies by using Natural Language Processing.
Enhancing Named Entity Recognition followed by Relation Extraction for entity types of 'PERSON', 'OBJECT', 'ANIMAL' and 'PLANT'.


-----------
# Requirements*:

python          3.8.12

pandas          1.3.3 

spacy           2.3.7 

scikit-learn       0.24.2

Mysql 



*Note that the implementation is not compatible with spacy 3.0+.



----

# Preparation

Note that all the procedure will be also shown in a jupyter notebook.

Establish a database connection. The class `Database Connection`(io.py) uses pandas to send queries to the mysql database. 

mysql_connection format: `mysql+mysqlconnector://USER@IP/DATABASE` (Replace USER,IP and DATABASE with your data.)

with the function `load_designs_from_db` a query can be send to select the table and columns, for example `.load_designs_from_db("designs", ["DesignID", "DesignEng"])`

The output will be a pandas dataframe.

with the function `load_entities_from_db`a query can be send to select the table that contains entities, note that the major difference between the this and `load_designs_from_db`is that the output is a list, instead of a dataframe. The function takes up to 6 parameters. The table name, a list of columns, a list of columns that contain multiple values in the string, a delimiter symbol, and a boolean if a delimiter exists or not. For example `load_entities_from_db("nlp_list_person", ["name", "alternativenames"], ["alternativenames"], ",", True)`



After loading the designs and the entities, the designs can be annotated with the `annotate_designs`function, this will annotate all entities in the designs that match with the entity list.

---

# Named Entity Recognition

The NER model can be created with the `Designestimator`class (model.py). The class takes up to 8 parameters:

- n_rep - Number of epochs
-  output_dir - directory to save the model
- model_name - a name which will be used for saving the model
- design_col - the column of the dataframe that contains the designs
- spacy_model - the spacy model to use, if no model is passed the english ('en_core_web_sm') will be loaded. (More information to the model at https://spacy.io/usage/models)
- learning_rate - the learning rate of the model, default 0.001
- batch_size - the batch size, default 100
- train -  if the model should be trainable or not, default True



Before training the entity labels need to be created, this can be done with `set_labels`, which needs a list with labels as input.

For example `my_estimator.set_labels("PERSON", "OBJECT", "ANIMAL", "PLANT")`

With `my_estimator.save_model(output_dir, model_name)`can be saved, after training the model will be automatically saved.

With `my_estimator.load_model(output_dir, model_name)`a model can be load

## Predictions 

There are two ways of using the predict function.

the first one (`predict(x)`)will return return a prediction having a triple with position and entity label.  

The second way is to set as_doc to True `model.predict(designs, as_doc=True)`which will return the predicted word in the sentence instead of the position. Using spacy this can also be visualized, this can be seen in the jupyter notebook (`NER`)

---



# Relation Extraction

The Relation Extraction needs annotated data, this is done manually. Prepare a yaml file in the following format:

`? 'Amphora with ribbed surface and crooked handles containing two ears of corn and poppy.':` 

`- [Amphora, holding, poppy]`

`- [Amphora, holding, ears of corn]`

Load the yaml file and the entities from the database.

Similar to the NER model, the RE model can be saved and loaded. Have a look on the Jupyter Notebook for a better walkthrough.







## Reference

- https://www.corpus-nummorum.eu/
- http://numismatics.org/ocre/
