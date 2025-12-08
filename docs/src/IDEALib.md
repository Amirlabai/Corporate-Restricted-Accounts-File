# Module `src/IDEALib.py`

## Functions

### `_connect_to_COM(comObjName)`

No description provided.

**Arguments:**
- `comObjName`

### `_connect_to_idea()`

No description provided.

### `_connect_to_InstallInfo()`

No description provided.

### `_connect_to_ConfigureIdea()`

No description provided.

### `_connect_to_ideaRDF()`

No description provided.

### `idea_marketing_version()`

No description provided.

### `idea_version()`

No description provided.

### `idea_language()`

No description provided.

### `idea_encoding()`

No description provided.

### `list_separator()`

No description provided.

### `decimal_separator()`

No description provided.

### `_get_db_extension()`

No description provided.

### `_get_working_directory()`

No description provided.

### `_read_registry(key, subkey, keyValue)`

No description provided.

**Arguments:**
- `key`
- `subkey`
- `keyValue`

### `_get_date_format(keyValue)`

No description provided.

**Arguments:**
- `keyValue`

### `short_date_format()`

No description provided.

### `long_date_format()`

No description provided.

### `_get_keys_by_value(dict, value)`

No description provided.

**Arguments:**
- `dict`
- `value`

### `_remove_prefix(text, prefix)`

No description provided.

**Arguments:**
- `text`
- `prefix`

### `_get_date_time_masks()`

No description provided.

### `idea_client()`

No description provided.

### `_export_database_from_IDEA(db, client, tempPath)`

No description provided.

**Arguments:**
- `db`
- `client`
- `tempPath`

### `_map_database_col_types(db, client)`

No description provided.

**Arguments:**
- `db`
- `client`

### `_import_csv_as_dataframe(csvPath, colMapping, dateMapping)`

No description provided.

**Arguments:**
- `csvPath`
- `colMapping`
- `dateMapping`

### `_clean_imported_times(df, times)`

No description provided.

**Arguments:**
- `df`
- `times`

### `_clean_imported_dates(df, dates)`

No description provided.

**Arguments:**
- `df`
- `dates`

### `_convert_characters_to_categories(df, characters)`

No description provided.

**Arguments:**
- `df`
- `characters`

### `_convert_character_to_datetime(df, mapping, datefieldnames)`

No description provided.

**Arguments:**
- `df`
- `mapping`
- `datefieldnames`

### `idea2py(database=None, client=None)`

No description provided.

**Arguments:**
- `database` (default: `None`)
- `client` (default: `None`)

### `_convert_masked_column(colName, mask, type, tableDef, tableMgt)`

No description provided.

**Arguments:**
- `colName`
- `mask`
- `type`
- `tableDef`
- `tableMgt`

### `_import_csv_into_idea(csvPath, tempPath, databaseName, client, df, dateFields, timeFields)`

No description provided.

**Arguments:**
- `csvPath`
- `tempPath`
- `databaseName`
- `client`
- `df`
- `dateFields`
- `timeFields`

### `_export_dataframe_to_csv(df, tempPath)`

No description provided.

**Arguments:**
- `df`
- `tempPath`

### `_clean_boolean_values(bool)`

No description provided.

**Arguments:**
- `bool`

### `_clean_timedelta_values(x)`

No description provided.

**Arguments:**
- `x`

### `_is_valid_time_column(colTime)`

No description provided.

**Arguments:**
- `colTime`

### `_clean_dataframe_for_export(df)`

No description provided.

**Arguments:**
- `df`

### `py2idea(dataframe, databaseName, client=None, createUniqueFile=False)`

No description provided.

**Arguments:**
- `dataframe`
- `databaseName`
- `client` (default: `None`)
- `createUniqueFile` (default: `False`)

### `refresh_file_explorer(client=None)`

No description provided.

**Arguments:**
- `client` (default: `None`)

### `_folder_is_invalid(path)`

No description provided.

**Arguments:**
- `path`

### `_file_is_invalid(file)`

No description provided.

**Arguments:**
- `file`

### `project_files()`

No description provided.

## Classes

### `_SingletonIdeaClient`

No description provided.

#### Methods

- `get_instance()`
  - No description provided.

- `get_client()`
  - No description provided.

- `__init__(self)`
  - No description provided.
  - Arguments:
    - `self`
