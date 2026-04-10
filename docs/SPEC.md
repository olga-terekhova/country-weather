# Specification

## REQ-1. Fetch page by url
Create a PS1 script in the `page/` directory. 

### Assumptions
1. Within the script, consider the caller's current working directory as local. 

### Parameters
1. The script has one required input parameter of string type with a file name. The parameter is a filename - relative to the local directory. For example: `page_list.txt`. 

2. The script has one optional input parameter of integer type with a wait time expressed as a number of seconds. 10 by default, overridable by the caller.

### Input data
The input file should have an extension.
The file is assumed to be a text file containing a list of sites in the form of a URL and a filename.
Each site is on a separate line. 
The URL and the file name of the same site are on the same line, separated by a space. 

For example:
```
https://example.com example.html
https://google.com google.html
```

### Work to be done
The script creates a new directory in the local directory. The name of the directory is derived from the filename minus the extension. 
For example, `page_list.txt` -> `page_list` directory.  

If the directory already exists, show an error to host and stop the execution.

For each line in the file, the script invokes a request to download the page using the URL from the line and saves the result (`.Content` string in UTF-8 encoding) into the file using the filename from the line, under the newly created directory. 
For example:
The content of `https://example.com` is saved to `page_list\example.html`.
The content of `https://google.com` is saved to `page_list\google.html`.

For malformed lines, show a warning to host, skip the line, continue with the next one. Examples of malformed: 
- empty line
- line with only one token
- lines with more than two tokens

If there are connection-level failures (Invoke-WebRequest throws an exception), show in the error stream, skip the line, continue with the next one (don't exit). 

No validation as to the server answer needed, save response as is.

If the target file already exists, show the warning into the host, overwrite the file, continue.

Display informational messages "X page saved to Y" after download + save. 

Between every two consecutive downloads the script pauses for the duration of the waitTime. 
Display information message "Waiting N seconds before the next download".

Follow the best practices for PowerShell scripts. Name the variables clearly and according to the conventions. 

## REQ-2. Extract list of cities' URLs
Create a PowerShell script in the 'prepare/' directory.

### Assumptions
1. Within the script, consider the caller's current working directory as local. 
2. Use PowerShell 5.1 compatible functions. 

### Parameters
1. The script has a required input parameter of string type. The parameter is the source file path - relative to the local directory or absolute. For example: `country.html` or `C:\temp\country.html`.

2. The script has a required input parameter of string type. The parameter is the output file path - relative to the local directory or absolute. For example: `country.csv` or `C:\temp\country.csv`.

3. The script has one required parameter of string type. The parameter is the URL which should be appended to relative links in the html file to resolve them into absolute URLs (url-append). 

### Preprocess
1. Identify whether the provided source file path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the host. Check that file exists and exit if it doesn't. 
2. Identify whether the provided output file path is relative or absolute. If it is relative - resolve it relative to the local directory. Create the needed directories in the path if they do not exist, surface it in the informational stream. 
3. If the user submitted the url-append with a trailing slash (for example, `https://example.com/`), remove the trailing slash. 

### Input data
The file path is assumed to point to an html file. The html file is assumed to contain several links in the format of <a href="/prognoz/city-name/">.

### Process
1. Read the file from the preprocessed source file path. 
2. Collect substrings that conform to an expression `<a href="/prognoz/*/">` (this structure exactly). For example `<a href="/prognoz/city-name/">`.
3. For each line in the collection
- extract a variable city-name as the value between `/prognoz/` and `/`
- extract a variable city-url as a concatenation of url-append and the value of href. 
4. Do not perform duplication checks.
5. Save the resulting table as a CSV file with headers `city-name` and `city-url` and a default UTF encoding. The file is saved to the preprocessed output file path.
  - If the target file already exists, show the warning into the host, overwrite the file, continue.
  - Show the informational message with a number of cities saved to file. 

## REQ-3. Create a table with cities and months cross joined. 
Create a Python script in `prepare/` that cross joins a csv with cities with a csv with months.

### Assumptions
1. duckdb installed by `uv add duckdb`.
2. User created a file `months.csv` with the list of strings encoding month x year pairs. 
3. csv files have headers.

### Parameters
1. cities-csv (string), optional, defaults to `cities/cities.csv`.
2. months-csv (string), optional, defaults to `months/months.csv`.
3. cities-months-csv (string), optional, defaults to `cities-months/cities-months.csv`.

### Preprocess
1. Identify whether the provided cities-csv path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. Check that file exists and exit if it doesn't. 
2. Identify whether the provided months-csv path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. Check that file exists and exit if it doesn't.
3. Identify whether the provided cities-months-csv path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. Create the needed directories in the path if they do not exist, surface it in the informational stream. 

### Process
1. Use duckdb to run the query:
```
SELECT 
    cities."city-name",
    months.month,
    cities."city-url" || months.month || '/' as "city-month-url",
    cities."city-name" || '-'|| months.month || '.html' as "city-month-file"
    
FROM read_csv_auto('{cities-csv}') as cities CROSS JOIN read_csv_auto('{months-csv}') as months

```
`{cities-csv}` and `{months-csv}` is pseudo-code as placeholders for file paths after preprocessing.

2. Write the result in a CSV format to the file specified by `cities-months-csv` path. Enforce wrapping in `"` quotes. If the file already exists, overwrite. 

### Instructions
Follow the best practices for Python scripts. Name the variables and functions clearly and according to the conventions. 



## REQ-4. Fetch pages from a CSV
Create a PowerShell script in the `page/` directory that downloads pages using a collection of URL + filenames in a CSV file. This is a functionality similar to the REQ-1 function (`page/Fetch-Pages.ps1`). 

### Assumptions
1. Within the script, consider the caller's current working directory as local. 
2. Use PowerShell 5.1 compatible functions. 

### Parameters
1. The script has a required input parameter of string type. The parameter is the source file path - relative to the local directory or absolute. For example: `cities-months.csv` or `C:\temp\cities-months.csv`.

2. The script has a required input parameter of string type with the name of the column with an URL. For example, "city-month-url".

3. The script has a required input parameter of string type with the name of the column with a file name. For example, "city-month-file".

4. The script has one optional input parameter of integer type with a wait time expressed as a number of seconds. 10 by default, overridable by the caller.

5. The script has one optional input parameter of string type with a range to select rows from the collection, with a start and stop separated by ':'. For example, "1:10" or ":2". Empty start equals 0, Empty stop equals the number of the rows. Defaults to ":", which would mean all rows except the headers. 0 would be a first line after the headers. Stop bound is exclusive.  

### Preprocess
1. Identify whether the provided source file path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the host. Check that file exists and exit if it doesn't. 

2. Derive a name for a new directory. The name of the directory is the source filename minus the extension (filename only is relevant here, not the full path). 
For example, `cities-months.csv` -> `cities-months` directory. 
Create this directory in the local directory. 
If the directory already exists, write a warning to host, but continue.

3. Parse the values in the range parameter to define start and stop. If the string cannot be parsed, write error to host and exit execution. 

### Input data
The input file should be a csv file.
The file is assumed to be have the columns specified in the parameters.


### Process
1. Read the input file specifed in the parameter 1. Use only the columns specified in the parameters 2 and 3. Read only the range of rows defined by the parameter 5. Create a collection for the resulting table, where each row has URL + filename. 

If the file does not have needed columns, show an error and exit execution.
If the file does not have the specified range of rows, even if there is an overlap, show an error and exit execution.
If the file is empty, or only has a row of headrs, show an error and exit execution.

2. For each line in the collection, the script invokes a request to download the page using the URL from the line and saves the result (`.Content` string in UTF-8 encoding) into the file using the filename from the line, under the newly created directory. 
For example:
The content of `https://example.com` is saved to `page_list\example.html`.
The content of `https://google.com` is saved to `page_list\google.html`.

If there are connection-level failures (Invoke-WebRequest throws an exception), show in the error stream, skip the line, continue with the next one (don't exit). 

No validation as to the server answer needed, save response as is.

If the target file already exists, show the warning into the host, overwrite the file, continue.

Display informational messages "$url saved to $outputFilePath" after download + save. 

Between every two consecutive downloads (no matter whether succeeded or not) the script pauses for the duration of the waitTime. 
Display information message "Waiting N seconds before the next download".

Follow the best practices for PowerShell scripts. Name the variables clearly and according to the conventions.

## REQ-5. Extract weather data from cities-months html files
Create a Python script in `prepare/` directory which creates a csv file with weather data for each cities-month html file. 

### Assumptions
1. BeautifulSoup installed by `uv add beautifulsoup4`.

### Parameters
1. The script has one required parameter of the string type. This is a path to a directory containing html files - either relative or absolute. For example, `cities-months`.

### Preprocess
1. Identify whether the provided directory path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. Check that the directory exists and exit if it doesn't.

### Process
For each '.html' file in the directory:
1. Verify that the name of the file matches the format "[string1]-[string2]-[string3].html"
    - if false, write error to host and stop execution
    - if true, define `city-name` as [string1], `month` as [string2], `year` as [string3]
2. Read the file and use BeautifulSoup to extract data in a tabular format:
    - each row corresponds to a day in a month
    - columns:
      - `city-name`
      - `month`
      - `year`
      - `day-number` - for example, 1 to 31)
      - `max-temperature` - corresponds to the day temperature forecasted on that day (for example, 30). Preserve sign for reusability. 
      - `max-humidity` - corresponds to the maximum humidity forecasted on that day (for example, 40). Omit the percentage, keep the number. 
    - all columns are integer
3. No checks for missing days are needed.
4. Save the file as a csv file with the same base name as the source, i.e. "[string1]-[string2]-[string3].csv", in the same directory. Overwrite file if exists. 

## REQ-6. Create a single dataset with weather data
Create a Python script in `prepare/` which writes separate csv files into one (union all datasets into one).

### Parameters
1. The script has one required parameter of the string type. This is a path to a directory containing csv files - either relative or absolute. For example, `cities-months`.
2. One optional requirement of the string type, which is a path to the output file. Defaults to `cities-days/cities-days.csv`.

### Assumptions

### Preprocess
1. Identify whether the provided directory path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. Check that the directory exists and exit if it doesn't.
2. Identify whether the provided cities-days path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. Create the needed directories in the path if they do not exist, surface it in the informational stream. 

### Process

Create the output file at the path defined by the preprocessed parameter 2. Overwrite the file if exists. Write headers: `city-name`, `month`, `year`, `day-number`, `max-temperature`, `max-humidity`.

For each '.csv' file in the input directory (sorted by name in ascending alphabetical order):
1. Verify that it has the same schema as the headers in the output file: same columns names in the same order. 
  - If false, write warning in the host, skip the file.
  - If true, write all non-header rows into the output file. 
Checks:
  - No duplicate checks needed. 
  - If the file has headers in the correct schema but is otherwise empty, write warning to the host and continue. 

## REQ-7. Create JSON layer for presenting data in pre-indexed aggregates
Create a Python script in `present/` directory. 

### Parameters
1. A required string parameter for the source file path. For example, 
2. A requred string paramater fro the output files directory.

### Preprocess
1. Identify whether the provided source file path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. 
Checks:
- Verify that the file path exists, write error to host and exit if it doesn't.
- Verify that the file has the 'csv' extension, and the file is not empty. Write error to the console and exit if not true.
2. Identify whether the provided output directory path is relative or absolute. If it is relative - resolve it relative to the local directory. Write the resulting absolute path to the console. Create the needed directories in the path if they do not exist, surface it in the informational stream. 

### Process

1. Extract the daily dataset with the schema "year, month, day, city, temperature, humidity" using duckdb:

```
SELECT 
    year,
    month,
    "day-number" as day,
    "city-name" as city,
    "max-temperature" as temperature,
    "max-humidity" as humidity
FROM read_csv_auto('{source file path}')
ORDER BY 1, 2, 3, 4
```


2. Build a json out of the rows fetched by duckdb with a three-layer hierarchy: "YYYY-MM" -> day (int-like string) -> [city records].
First layer key: `f"{year}-{month:02d}"`
Second layer key: day
Third layer keys: city, temperature, humidity

An example of the resulting structure:
```
{
  "2024-01": {
    "1":  [ { "city": "Toronto", "temperature": -3, "humidity": 71 }, ... ],
    "2":  [ ... ],
    ...
    "31": [ ... ]
  },
  "2024-02": {
    "1":  [ ... ],
    ...
  }
}
```

3. Write the three layered json into the file `daily.json` in the output directory. Overwrite if the file exist.

## REQ-8. Create a container to serve a small server with html, js, and json
Create new files: 
  - serve/Dockerfile - minimal Node.js image with serve installed globally via `npm install -g serve`, running serve -p 3000 . as the default command 
  - serve/docker-compose.yml - defines a single service that builds from ./serve, mounts ../present/daily into the container at /app, sets /app as the working directory, and maps host port 3000 to container port 3000                                                
                                                             
Runtime behavior: running docker compose up from the host inside the serve/ directory (or with -f serve/docker-compose.yml) starts a container that statically serves the contents of present/daily/ - including daily.json and future HTML and JS files - at http://localhost:3000.    

## REQ-9. Visualize daily city weather scatter plot
1. Create `present/daily/index.html` and necessary JS files to render a visualization of data in `present/daily/daily.json`. 
2. Assume all files are in `present/daily/`, use relative paths. 
3. Use D3 for visualization. 
4. Visuals on the page:
  - a dropdown labeled "Year and Month" directly above the plot rectangle
    - width 100 px
  - a dropdown labeled "Track city" below "Year and Month"
    - width 100 px
  - a horizontal slider below "Track city"
    - implemented as `HTML <input type="range">`
    - width 800 px
    - an empty placeholder label for the start of the month on the left
    - an empty placeholder label for the end of the month on the right
    - an empty placeholder label for the current day directly above the slider caret
  - a rectangle for the scatter plot below the slider
    - dimensions are 800 x 500
    - X axis is "Humidity, %"
    - Y axis is "Temperature, °C"
  
5. Data init:
  - read `daily.json` at the page load
    - first level has year-month values, like "2025-08"
    - second level has int-like day values, like "1", "20"
    - third level has several items for city and weather data for that year, month and day, like {"city": "toronto", "temperature": 37, "humidity": 30}
  - get the min and max values for temperature and humidity from the whole dataset
    - define the visible dimensions of both axis as [min value of the metric - 10%; max value of the metric + 10%]
    - add evenly spaced ticks on the plot axes
    - formulate how to translate any given pair of humidity and temperature into the coordinates on the scatter plot
  - collect the first level keys from the json as year-month strings
  - populate the dropdown values with the year-month strings
  - set the current year-month value as the first item in the collection
  - set the current day as the first day in the current month
  - trigger a redraw of the slider and of the scatter plot
6. Visualization
  - slider:
    - get the collection of days in the current year-month
    - set current day at the first day in the collection
    - break down the slider horizontal line into the number of days in the current month
    - populate the labels for start, stop, current day
    - draw the slider caret at current day
  - scatter plot
    - get the collection of city data in the current year, month and day
    - for each item: 
      - calculate X and Y based on the values of humidity and temperature
      - put a dot labeled with the city name (city name always visible)
      - assign a label on hover with the exact values of city name, humidity and temperature
7. User interactions:
  - a user can select a year-month string from the dropdown which triggers an update of slider and scatter plot for the 1st day of this month
  - a user can move the slide between the start and end values for the current month, which triggers a redraw of the scatter plot for this day
