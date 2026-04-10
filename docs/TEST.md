## REQ-1
cd page
.\Fetch-Pages.ps1 country.txt

## REQ-2
cd prepare
.\Get-CitiesFromHtml.ps1 -SourcePath ..\page\country\country.html -OutputPath cities\cities.csv -UrlAppend https://pogoda.mail.ru/

## REQ-3
cd /projects/country-weather/prepare && uv run python cross_join_cities_months.py

## REQ-4
cd prepare/cities-months
../../page/Fetch-Pages-CSV.ps1 -SourceFilePath cities-months.csv -UrlColumn city-month-url -FileNameColumn city-month-file -Range :2 -WaitSeconds 5

cd page
.\Fetch-Pages-CSV.ps1 -SourceFilePath ..\prepare\cities-months\cities-months.csv -UrlColumn city-month-url -FileNameColumn city-month-file -Range :2 -WaitSeconds 5

## REQ-5
uv run prepare/extract_weather.py page/cities-months && head -3 page/cities-months/abovyan-august-2025.csv

## REQ-6
uv run prepare/union_weather.py page/cities-months --output /tmp/cities-days-test.csv 2>&1
wc -l /tmp/cities-days-test.csv && head -2 /tmp/cities-days-test.csv && tail -2 /tmp/cities-days-test.csv 

uv run prepare/union_weather.py page/cities-months --output prepare/cities-days/cities-days-test.csv