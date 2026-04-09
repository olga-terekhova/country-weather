## REQ-1
cd page
.\Fetch-Pages.ps1 country.txt

## REQ-2
cd prepare
.\Get-CitiesFromHtml.ps1 -SourcePath ..\page\country\country.html -OutputPath cities\cities.csv -UrlAppend https://pogoda.mail.ru/

## REQ-3
cd /projects/country-weather/prepare && uv run python cross_join_cities_months.py