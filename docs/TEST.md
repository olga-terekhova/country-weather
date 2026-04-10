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
### First test
uv run prepare/union_weather.py page/cities-months --output /tmp/cities-days-test.csv 2>&1
wc -l /tmp/cities-days-test.csv && head -2 /tmp/cities-days-test.csv && tail -2 /tmp/cities-days-test.csv 

### Target
uv run prepare/union_weather.py page/cities-months --output prepare/cities-days/cities-days.csv

## REQ-7
### First test
uv run present/build_daily_json.py prepare/cities-days/cities-days.csv /tmp/weather-out
python3 -c "
import json
with open('/tmp/weather-out/daily.json') as f:
    d = json.load(f)
keys = list(d.keys())
print('Top-level keys:', keys)
first = keys[0]
day_keys = list(d[first].keys())
print(f'Day keys for {first}:', day_keys[:5])
print(f'Sample record:', d[first][day_keys[0]][0])
"

### Error: file not found
uv run present/build_daily_json.py nonexistent.csv /tmp/x

### Error: file is empty
touch /tmp/empty.csv && uv run present/build_daily_json.py /tmp/empty.csv /tmp/x

### Target
uv run present/build_daily_json.py prepare/cities-days/cities-days.csv present/daily

## REQ-8
Host machine shell:

cd serve
docker compose up -d

Host machine browser:

http://localhost:3000

## REQ-9
From present/daily:
Invoke-WebRequest -Uri "https://d3js.org/d3.v7.min.js" -OutFile "d3.v7.min.js" -UseBasicParsing