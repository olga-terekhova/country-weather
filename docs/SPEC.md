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
The script creates a new directory in the local directory. The name of the directory is derived from the filename minus the extenstion. 
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