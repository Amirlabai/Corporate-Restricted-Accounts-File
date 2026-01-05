
# region Imports
import logging
import os
import os.path as path
import tempfile
import csv
import winreg
import time
import locale

import pandas as pd
import numpy as np
import win32com.client as win32com
# endregion
__version__ = "2.0.0"

# Constants for filtering project_files()
FILEFILTER   = ["Project.lock", "ProjectOverview.sdf", "ProjectOverview.db"]
FOLDERFILTER = ["__pycache__"]
PREFIXFILTER = ["~"]
PATHSEPERATOR = os.path.sep

# region Setup
'''logging.basicConfig(
    filename="IDEALib.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)'''

# Use appropriate delimiter and decimal separator values based on set locale
DELIMITER = ','
locale.setlocale(locale.LC_ALL, '')
DECIMAL_SEPARATOR = locale.localeconv()["decimal_point"]
if locale.localeconv()["decimal_point"] != '.':
    DELIMITER = ';'

# endregion

# region Classes
class _SingletonIdeaClient:
    __instance = None
    __client = None

    @staticmethod
    def get_instance():
        if _SingletonIdeaClient.__instance is None:
            _SingletonIdeaClient()
        return _SingletonIdeaClient.__instance

    @staticmethod
    def get_client():
        if _SingletonIdeaClient.__instance is None:
            _SingletonIdeaClient()
        return _SingletonIdeaClient.__client

    def __init__(self):
        if _SingletonIdeaClient.__instance is not None:
            msg = "This class is a singleton and already has an instance"
            #logging.warning(msg)
            raise Exception(msg)
        else:
            _SingletonIdeaClient.__instance = self
            _SingletonIdeaClient.__client = _connect_to_idea()


# endregion

# region IDEA COM Functions

def _connect_to_COM(comObjName):
    try:
        comObj = win32com.Dispatch(dispatch=comObjName)
    except Exception as e:
        msg = f"Unable to connect to {comObjName}: {e}"
        #logging.error(msg)
        raise Exception(msg)
    return comObj

# Returns IDEA Client object
def _connect_to_idea():
    return _connect_to_COM("Idea.IdeaClient")

# Returns InstallInfo COM Object
def _connect_to_InstallInfo():
    return _connect_to_COM("Idea.InstallInfo")

# Returns ConfigureIdea COM Object
def _connect_to_ConfigureIdea():
    return _connect_to_COM("Idea.ConfigureIdea")

def _connect_to_ideaRDF():
    return _connect_to_COM("Idea.IDEARDF")

# endregion

# region IDEA Properties

def idea_marketing_version():
    #logging.info("IDEAMarketingVersion: Function Called")
    try:
        installInfo = _connect_to_InstallInfo()
        value = installInfo.MarketingVersion
    except Exception as e:
        #logging.error(f"IDEAMarketingVersion: Error - {e}")
        raise
    finally:
        del installInfo

    #logging.info("IDEAMarketingVersion: Successful")
    return value

def idea_version():
    #logging.info("IDEAVersion: Function Called")
    try:
        installInfo = _connect_to_InstallInfo()
        value = installInfo.Version
    except Exception as e:
        #logging.error(f"IDEAVersion: Error - {e}")
        raise
    finally:
        del installInfo

    #logging.info("IDEAVersion: Successful")
    return value

def idea_language():
    #logging.info("IDEALanguage: Function Called")
    try:
        installInfo = _connect_to_InstallInfo()
        value = installInfo.AppLanguage
    except Exception as e:
        #logging.error(f"IDEALanguage: Error - {e}")
        raise
    finally:
        del installInfo

    #logging.info("IDEALanguage: Successful")
    return value

def idea_encoding():
    #logging.info("IDEAEncoding: Function Called")
    try:
        installInfo = _connect_to_InstallInfo()
        value = installInfo.AppStandard
    except Exception as e:
        #logging.error(f"IDEAEncoding: Error - {e}")
        raise
    finally:
        del installInfo

    #logging.info("IDEAEncoding: Successful")
    return value

def list_separator():
    #logging.info("ListSeparator: Function Called")
    try:
        configureIdea = _connect_to_ConfigureIdea()
        value = configureIdea.ListSeparator
    except Exception as e:
        #logging.error(f"ListSeparator: Error - {e}")
        raise
    finally:
        del configureIdea

    #logging.info("ListSeparator: Successful")
    return value

def decimal_separator():
    #logging.info("DecimalSeparator: Function Called")
    try:
        configureIdea = _connect_to_ConfigureIdea()
        value = configureIdea.DecimalSeparator
    except Exception as e:
        #logging.error(f"DecimalSeparator: Error - {e}")
        raise
    finally:
        del configureIdea

    #logging.info("DecimalSeparator: Successful")
    return value

'''
Reads ConfigureIDEA to find out the file extension
Returns the appropriate file extension
'''
def _get_db_extension():
    try:
        configureIdea = _connect_to_ConfigureIdea()
        value = configureIdea.IDEADBExt
    except Exception as e:
        #logging.error(f"_get_db_extension: Error - {e}")
        raise
    finally:
        del configureIdea

    return value.lower() # calling to lower to perserve how the function previously return

def _get_working_directory():
    try:
        configureIdea = _connect_to_ConfigureIdea()
        value = configureIdea.WorkingDirectory
    except Exception as e:
        #logging.error(f"_get_working_directory: Error - {e}")
        raise
    finally:
        del configureIdea

    return value
# endregion

# region Globalization Functions
def _read_registry(key,subkey,keyValue):
    value = None
    try:
        registry_key   = winreg.OpenKey(key, subkey, 0, winreg.KEY_READ) 
        value, regtype = winreg.QueryValueEx(registry_key, keyValue)
        winreg.CloseKey(registry_key)
    except:
        msg = "_read_registry: Error Reading the registry key '" + subkey + "\\" + keyValue + "'"
        #logging.error(msg)
        value = None
    return value

def _get_date_format(keyValue):
    key = winreg.HKEY_CURRENT_USER
    subkey = "Control Panel\\International"

    return _read_registry(key, subkey, keyValue)

def short_date_format():
    #logging.info("short_date_format: Function Called")

    keyValue = "sShortDate"
    value = _get_date_format(keyValue)

    #logging.info("short_date_format: Successful")    
    return value

def long_date_format():
    #logging.info("long_date_format: Function Called")

    keyValue = "sLongDate"
    value = _get_date_format(keyValue)

    #logging.info("long_date_format: Successful")
    return value

# endregion

# region Helper Functions

def _get_keys_by_value(dict,value):
    dictAsList = dict.items()
    keys = []
    for item in dictAsList:
        if item[1] is value:
            keys.append(item[0])
    return keys

def _remove_prefix(text,prefix):
    if text.startswith(prefix):
        text = text[len(prefix):]
    return text

def _get_date_time_masks():
    lang = idea_language().upper()
    # Mask for EN, DE, JA and NL
    dateMask = "yyyy-mm-dd"
    timeMask = "HH:MM:SS"

    if lang == "FR":
        dateMask = "aaaa-mm-jj"
        timeMask = "HH:MM:SS"
    elif lang == "ES" or lang == "PT":
        dateMask = "aaaa-mm-dd"
        timeMask = "HH:MM:SS"
    elif lang == "HU":
        dateMask = "éééé-hh-nn"
        timeMask = "ÓÓ:PP:MM"
    elif lang == "CS":
        dateMask = "rrrr-mm-dd"
        timeMask = "HH:MM:SS"
    elif lang == "JA-JP":
        dateMask = "ﾎﾎﾎﾎ-mm-dd"
        timeMask = "HH:MM:SS"
    elif lang == "RU-RU":
        dateMask = "ЖЖЖЖ-mm-dd"
        timeMask = "HH:MM:SS"
        
    return dateMask, timeMask

# endregion

# region IDEA Client functions

def idea_client():
    #logging.info("idea_client: Function Called")
    return _SingletonIdeaClient.get_client()

# endregion
# region Get Data From IDEA
def _export_database_from_IDEA(db,client,tempPath):    
    exportPath = path.join(tempPath,"tempExport.del")     
    task = db.ExportDatabase()    
    task.IncludeAllFields()
    task.IncludeFieldNames ="TRUE"
    eqn = ""
    task.Separators(DELIMITER,DECIMAL_SEPARATOR)

    task.PerformTask(exportPath,"Database","DEL UTF-8",1,db.Count,eqn)

    return exportPath    

## Goes through the database and returns a list of all the date columns, time columns,
## and a dictionary of all the other columns paired with their respective pandas type     
##
## IDEA Type             => Panda Type
## ---------------------------------------
## Character < 2500 vals => category
## Other Character       => object
## Numeric w/ 0 decimals => int64
## Numeric w/ decimals   => float64
## Date                  => datetime64
## Time                  => timedelta
## Multistate            => int8
## Boolean               => bool
def _map_database_col_types(db,client):
    # Define constants
    WI_VIRT_CHAR  = 0
    WI_VIRT_DATE  = 2
    WI_VIRT_NUM   = 1
    WI_VIRT_TIME  = 13
    
    WI_BOOL       = 10
    WI_MULTISTATE = 9

    WI_EDIT_CHAR  = 3
    WI_EDIT_DATE  = 5
    WI_EDIT_NUM   = 4
    WI_EDIT_TIME  = 11
    
    WI_DATE_FIELD = 5
    WI_CHAR_FIELD = 3
    WI_NUM_FIELD  = 4
    WI_TIME_FIELD = 11

    TIMES = [WI_VIRT_TIME, WI_EDIT_TIME, WI_TIME_FIELD]
    CHARS = [WI_VIRT_CHAR, WI_EDIT_CHAR, WI_CHAR_FIELD,WI_VIRT_DATE, WI_EDIT_DATE, WI_DATE_FIELD]
    NUMS  = [WI_VIRT_NUM, WI_EDIT_NUM, WI_NUM_FIELD]
    fieldType = [WI_VIRT_DATE, WI_EDIT_DATE, WI_DATE_FIELD]

    tableDef = db.TableDef()    
    numCols = tableDef.Count
    columnPairs={}
    dates = []
    times = []
    fieldName=[]

    for i in range(numCols):
        col = tableDef.GetFieldAt(i+1)
        if col.Type in CHARS:
            columnPairs[col.Name] = object
        elif col.Type in NUMS:
            columnPairs[col.Name] = np.int64 if (col.Decimals == 0) else np.float64            
        elif col.Type  in TIMES:            
            times.append(col.Name) 
        elif col.Type is WI_BOOL:
            columnPairs[col.Name] = bool
        elif col.Type is WI_MULTISTATE:
            columnPairs[col.Name] = np.int8

        if col.Type in fieldType:
            fieldName.append(col.Name)

    return columnPairs, dates, times,fieldName

def _import_csv_as_dataframe(csvPath,colMapping,dateMapping):
    dataframe = pd.read_csv(csvPath, dtype=colMapping, parse_dates=dateMapping, 
                                encoding='UTF–8', sep=DELIMITER, decimal=DECIMAL_SEPARATOR, quotechar='"', quoting = csv.QUOTE_NONNUMERIC)
    return dataframe

# Converts the time fields from datetime to time only. Prevents data from being defaulted to date of import
def _clean_imported_times(df,times):
    for column in times:
         df[column] = pd.to_timedelta(df[column])
    return None

# Check if it imported correctly, if not try to parse it again in more detail
def _clean_imported_dates(df,dates):
    for column in dates:
        if 'datetime64' not in df[column].dtype.name:
            df[column]=pd.to_datetime(df[column])
    return None

# Based on type conversion, set any columns that were CHARACTERS and had less that 250 unique values to type category
def _convert_characters_to_categories(df,characters):
    UNIQUE_VALUE_THRESHHOLD = 2500
    for col in characters:
        if df[col].nunique() < UNIQUE_VALUE_THRESHHOLD:
            df[col] = df[col].astype('category')
    return None

def _convert_character_to_datetime(df,mapping,datefieldnames):
    for field in datefieldnames:
        if field in mapping:
            del mapping[field]
        df[field] = df[field].replace({'00000000': np.nan})
        df[field] = pd.to_datetime(df[field], format='%Y%m%d', errors='coerce')

'''
Takes an IDEA database file and imports it into a Panadas Dataframe

Parametes:
database - Path to the database, if only a file is given it will assume that it is the current working directory, if empty it will use current database.
header   - Boolean that determines if the database should be exported with first row as field names, defualts to True.
client   - COM Client object of IDEA, if not supplied it will create a new COM connection and use that.

Returns: Dataframe of the IDEA database
'''
def idea2py(database=None, client=None):
    #logging.info("idea2py: Function Called")
    EMPTY = ""    
    if client is None:
        client = idea_client()        
    
    if database is None:
        try:
            database = client.CurrentDatabase().Name            
        except:            
            database = client.CommonDialogs().FileExplorer()            
            if database is EMPTY:
                msg = "You must select an IDEA database."
                #logging.warning(msg)
                return None
            database = database.replace('/','\\')        
    
    root,ext = path.splitext(database)
    if ext is None or (ext.lower() != ".imd" and ext.lower() != ".idm"):
        ideaExtension = _get_db_extension()
        if ideaExtension is None:
            msg = "Error reading the IDEA Database Extension."
            #logging.error(msg)
            return None        
        database = root+ideaExtension

    try:
        db = client.OpenDatabase(database)
    except:
        msg = f"An error occurred while opening the {database} database."
        #logging.error(msg)
        return None

    if db.Count == 0:
        msg = f"The {database} database has no records."
        #logging.error(msg)
        return None
    #logging.info("idea2py: Parameters verified.")      
    tempDir = tempfile.TemporaryDirectory()
    tempDirPath = tempDir.name
    try:
        tempPath = _export_database_from_IDEA(db,client,tempDirPath)
        #logging.info("idea2py: IDEA Database exported to CSV.")

        mapping,dates,times,datefieldnames = _map_database_col_types(db,client)
        #logging.info("idea2py: IDEA column types mapped.")

        dataframe = _import_csv_as_dataframe(tempPath,mapping,dates)
        #logging.info("idea2py: CSV imported as a dataframe.")

        # convert character with date type data to datetime
        _convert_character_to_datetime(dataframe,mapping,datefieldnames)
        
        # clean up the database
        _clean_imported_times(dataframe,times)
        _clean_imported_dates(dataframe,dates)
        #logging.info("idea2py: Converted date and time columns to proper data type.")

        characters = _get_keys_by_value(mapping,object)
        _convert_characters_to_categories(dataframe,characters)
        #logging.info("idea2py: Eligible character columns converted to categories.")

    except Exception as e:
        msg = f"idea2py: IDEA database {database} could not be imported."
        #logging.error(msg)
        msg = f"Issue: {e}"
        #logging.error(msg)
        return None

    # Clean up resources
    tempDir.cleanup()
    #logging.info("idea2py: Successful")
    return dataframe

# endregion

# region Send Data To IDEA
'''
Converts an IDEA column to a type that requires a mask(date/time)
'''
def _convert_masked_column(colName,mask,type,tableDef,tableMgt):
    field = tableDef.NewField()

    field.Name = colName
    field.Description = ""
    field.Type = type
    field.Equation = mask

    tableMgt.ReplaceField(colName,field)
    tableMgt.PerformTask()

              

'''
Imports a csv into IDEA 
'''
def _import_csv_into_idea(csvPath,tempPath,databaseName,client,df,dateFields,timeFields):
    #Set extension for template depending if IDEA is Unicode or ASCII
    ideaExtension = _get_db_extension()
    if ideaExtension==".idm":
        rdfPath = path.join(tempPath,"temp_definition.rdm")
    else:
        rdfPath = path.join(tempPath, "temp_definition.rdf")

    dateMask,timeMask = _get_date_time_masks()

    types = df.dtypes
    columns = df.columns

    #Create template based onf fields in Dataframe
    idea = _connect_to_ideaRDF()
    idea.FileType=8
    idea.FieldSeparator = DELIMITER
    idea.RecordDelimiter = chr(13) + chr(10)
    idea.TextEncapsulator = chr(34)
    idea.HeaderLength = 0

    for col in range(len(columns)):
        columnType = str(types.iloc[col])
        columnName = columns[col]
        if columnName in dateFields:
            idea.appendfield(columnName, columnName, 5, 66, 8, 0, False, dateMask)
        elif columnName in timeFields:
            idea.appendfield(columnName, columnName, 117, 74, 11, 0, False, timeMask)
        elif columnType == 'category' and columnName not in dateFields :
            idea.appendfield(columnName, columnName, 1, 0, 1, 0, False,"")
        elif columnType == 'int64' or columnType == 'int32' or columnType == 'int32' or columnType == 'int8' or columnType == 'int':
            idea.appendfield(columnName, columnName, 2, 0, 1, 0, False, "")
        elif columnType == 'float64' or columnType == 'float32' or columnType == 'float16' or columnType == 'float8' or columnType == 'float' :
            #Logic to find maximum number of decimal places for floating numbers
            numericlist = df[columnName].tolist()
            maximumnumberofdecimalplaces = max(([len(str(i).rsplit('.', 1)[-1]) for i in numericlist]))
            #Check if maximum number of decimal places exceeds the limit in IDEA that is 6
            if maximumnumberofdecimalplaces > 6:
                maximumnumberofdecimalplaces=6
            idea.appendfield(columnName, columnName, 2, 0, 1, maximumnumberofdecimalplaces, False, "")
        else:
            idea.appendfield(columnName, columnName, 1, 0, 1, 0, False, "")

    idea.createfile(rdfPath)


    dbObj = None
    client.ImportUTF8DelimFile(csvPath,databaseName,True,"",rdfPath,False)
    dbObj = client.OpenDatabase(databaseName)        

    return dbObj
    

'''
Exports the dataframe to csv and returns the path to the file
'''
def _export_dataframe_to_csv(df,tempPath):
    exportPath = path.join(tempPath,"temp_export.csv")
    df.to_csv(path_or_buf=exportPath, sep=DELIMITER, index=False, header=False, encoding='utf-8', quotechar='"', decimal='.', quoting=csv.QUOTE_NONNUMERIC)

    return exportPath


'''
Takes in a bool and returns 1 for True, 0 for False.
'''
def _clean_boolean_values(bool):
    return int(bool)


'''
Takes in a timedelta and returns it in the format of HH:MM:SS.
'''
def _clean_timedelta_values(x):
    try:
        ts = x.total_seconds()
        hours, remainder = divmod(ts, 3600)
        minutes, seconds = divmod(remainder, 60)
        return ('{:02d}:{:02d}:{:02d}').format(int(hours), int(minutes), int(seconds)) 
    except:
        return None


def _is_valid_time_column(colTime):
    if(colTime.nunique() < 1):
        return False
    if(colTime.nunique() == 1 and ("00:00:00" in str(colTime.head(1)) or "NaT" in str(colTime.head(1)))):
       return False
    return True

'''
Cleans the incoming dataframe.

Splits up datetime fields into name_DATE, name_TIME, this is ignored if all the times are empty.
Converts all boolean to 1s for True, 0s for False.
Converts all the timedelta fields to the format of HH:MM:SS.

Returns the cleaned dataframe and a mapping of the columns.
'''
def _clean_dataframe_for_export(df):
    types = df.dtypes
    columns = df.columns
    dateFields = []
    timeFields = []
    toDrop = []
    map = {}

    for col in range(len(columns)):
        columnType = str(types.iloc[col])
        columnName = columns[col]

        
        if "datetime64" in columnType:
            #logging.info(f"clean dataframe: Splitting datetime fields for column {columnName}.")
            colMaster =  pd.to_datetime(df[columnName], errors='raise')
            colDate = colMaster.dt.date
            colTime = colMaster.dt.time
            
            #logging.info(f"clean dataframe: Time number of unique values: {colTime.nunique()}.")
            #logging.info(f"clean dataframe: Time first value: {str(colTime.head(1))}.")
            importTime = True

            if(not _is_valid_time_column(colTime)):
                #logging.info(f"clean dataframe: Checking if format of {colTime} is representing a datetime field.")
                importTime = False
            
            if importTime:
                #logging.info("clean dataframe: Setting name_DATE portion.")
                dateHeader = f"{columnName}_DATE"
                df.insert(col,dateHeader,colDate)
                map[dateHeader]="date"
                df[dateHeader] = df[dateHeader].astype(str)
                df[dateHeader] = df[dateHeader].str.replace('NaT', '', case=False)
                dateFields.append(dateHeader)
                
                #logging.info("clean dataframe: Setting name_TIME portion.")
                timeHeader = f"{columnName}_TIME"
                df.insert(col+1,timeHeader,colTime)
                map[timeHeader]="time"
                df[timeHeader] = df[timeHeader].astype(str)
                timeFields.append(timeHeader)

                #logging.info(f"clean dataframe: Datetime field new column name being: {columnName}")
                toDrop.append(columnName)
            else:
                #logging.info(f"clean dataframe: Determined {columnName} column is not a datetime field")
                df[columnName]=colDate
                map[columnName]="date"
                df[columnName] = df[columnName].astype(str)
                df[columnName] = df[columnName].str.replace('NaT', '', case=False)
                dateFields.append(columnName)
        else:
            if columnType == "bool":
                #logging.info(f"clean dataframe: Converting {columnName} to parseable boolean values")
                map[columnName]= "boolean"
                df[columnName] = np.vectorize(_clean_boolean_values)(df[columnName])
                 
            if columnType == "int8":
                 #logging.info(f"clean dataframe: Converting int8 {columnName} to parseable value")
                 map[columnName]= "multistate"

            if "timedelta" in columnType:
                #logging.info(f"clean dataframe: Converting timeDelta {columnName} to parseable value")
                map[columnName]= "time"
                df[columnName] = df[columnName].apply(_clean_timedelta_values)
                df[columnName] = df[columnName].astype('category')
                timeFields.append(columnName)
    df = df.drop(toDrop,axis=1)
    test=df.dtypes
    return df,map,dateFields,timeFields



'''
Takes in a dataframe,database name and idea client
Creates an IDEA database with the same name and data
Returns the IDEA database object if successful
'''
def py2idea(dataframe, databaseName, client=None, createUniqueFile = False):
    #logging.info("py2idea: Function Called")
    if client is None:
        client = idea_client()
    
    if databaseName is None:
        msg = "Missing database name."
        #logging.warning(msg)
        return None

    if dataframe is None:
        msg = "Missing dataframe."
        #logging.warning(msg)
        return None
    
    if len(dataframe) == 0:
        msg = "The dataframe has no records."
        #logging.warning(msg)
        return None       
    
    root,ext = path.splitext(databaseName)
    if ext is None or (ext.lower() != ".imd" and ext.lower() != ".idm"):
        ideaExtension = _get_db_extension()
        if ideaExtension is None:
            msg = "Error reading the IDEA Database Extension."
            #logging.error(msg)
            return None        
        databaseName = root+ideaExtension
    
   
    if databaseName.count("\\") == 0:
        # Assume it to be in the current working folder 
        workingDir = client.WorkingDirectory
        databaseName = path.join(workingDir,databaseName)

    if (path.exists(databaseName)):
        if (createUniqueFile):
            databaseName = client.UniqueFileName(databaseName)
        else:
            msg = f"IDEA database {databaseName} already exists"
            #logging.error(msg)
            return None
    
    tempDir = tempfile.TemporaryDirectory()
    tempPath = tempDir.name
    #logging.info("py2idea: Parameters verified")
    try: 
        dataframe,mapping,dateFields,timeFields = _clean_dataframe_for_export(dataframe)
        #logging.info("py2idea: Dataframe values cleaned for export.")
        csvPath = _export_dataframe_to_csv(dataframe,tempPath)
        db = _import_csv_into_idea(csvPath,tempPath,databaseName,client,dataframe,dateFields,timeFields)
        #logging.info("py2idea: CSV imported into IDEA.")

    except Exception as e:
        msg = f"py2idea: IDEA database {databaseName} could not be created."
        #logging.error(msg)
        msg = f"Issue: {e}"
        #logging.error(msg)
        return None
    
    tempDir.cleanup()
    #logging.info("py2idea: Successful")
    return db
# endregion

# region IDEA Client Functions

def refresh_file_explorer(client=None):
    #logging.info("RefreshFileExplorer: Function Called")
    if client is None:
        client = idea_client()
    client.RefreshFileExplorer()
    #logging.info("RefreshFileExplorer: Successful")


# endregion

# region File Management Functions

'''
Gathers all the files in the current IDEA working directory
Returns: A list of all the files with relative paths from the root of the current working directory
Filters:
Anything in the __pycache__ folder 
Project.lock file
ProjectOverview.sdf file
any file or folder that starts with ~
'''
def _folder_is_invalid(path):
    if len(path) == 0:
        return False
    for folder in path.split(PATHSEPERATOR):
        if((folder in FOLDERFILTER) or (folder[0] in PREFIXFILTER)):
            return True
    return False

def _file_is_invalid(file):
    return (file in FILEFILTER) or (file[0] in PREFIXFILTER)

def project_files():    
    #logging.info("ProjectFiles: Function Called")
    projectFiles = []
    directory = _get_working_directory() 

    for root,dirs,files in os.walk(directory,topdown=True):
        folder = _remove_prefix(root,directory) 
        if(_folder_is_invalid(folder)):
            continue
        for f in files:
            if (_file_is_invalid(f)):
                continue
            filepath = path.join(folder,f)
            projectFiles.append(filepath)

    #logging.info("ProjectFiles: Successful")
    return projectFiles

# endregion
#logging.info("")
#logging.info("----IDEALib.py Loaded----")