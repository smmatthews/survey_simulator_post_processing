"""
Extracts observation ID, limiting magnitude, and seeing from survey database, 
returing them as a 3*n pandas database.
"""

import pandas as pd
import sqlite3 as sql

def PPMatchFieldConditions(dbname, dbquery):

    """
    Input 
    -----

    dbname ...  string, name of survey database
    dgquery ... string, SQLite3 query for querying the pointing database (defined in configuration file)

    Output
    ------

    fieldConditions ... pandas dataframe containing field ID, limiting 
                        magnitude, and seeing

    """

    con = sql.connect(dbname)
    fieldConditions = pd.read_sql(dbquery, con)
    fieldConditions.rename(columns={"seeingFwhmEff" : "seeing"}, inplace=True)
    fieldConditions.rename(columns={"fiveSigmaDepth": "limiting magnitude"}, inplace=True)
    fieldConditions.rename(columns={"observationId" : "FieldID"}, inplace=True)

    seeing = fieldConditions.drop(columns=["limiting magnitude"])
    limiting_magnitude = fieldConditions.drop(columns=["seeing"])

    return seeing, limiting_magnitude