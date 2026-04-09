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
