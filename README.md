# pywu

pywu is a simple python script for fetching data from Weather Underground's API. You need an API key to use the script (get it [here](http://www.wunderground.com/weather/api/)).


### Config file

pywu supports reading from a config file as well as passing your API key/location via command line. A sample configuration:

~/.pywu.conf:
```
[PYWU]
apikey=<yourapikey>
location=New York City, NY
```


### Language Support

The default language for data returned from Weather Underground is English. You may specify a different language either on the command line (French for example):

`pywu fetch <apikey> <location> FR`

Or in the config file:
```
[PYWU]
...
language=FR
```

A list of possible language codes can be found [here](http://www.wunderground.com/weather/api/d/docs?d=language-support).


### Usage

Usage information can be found by passing the -h parameter or here:
```
usage: pywu.py [-h] [-v] [-f <min>] {fetch,current,forecast,info} ...

pywu pulls weather data from Weather Underground's API.

You must first fetch the data using the fetch command. This stores a file in /tmp that contains the data. All other commands (current, forecast, and info) read from this file.

positional arguments:
  {fetch,current,forecast,info}

        fetch: Pull weather data from server. Use the format '<API key> <city>,<state>' or simply your API key and zip code.

            pywu fetch <apikey> 'New York,NY'
            pywu fetch <apikey> 10001

            You can also specify a language (the default is English). For example:
            pywu fetch <apikey> <location> FR

            For a list of language codes, visit:
            http://www.wunderground.com/weather/api/d/docs?d=language-support

            Instead of the above, you may also use a ~/.pywu.conf file and simply call `pywu fetch`.


        current: Display current statistics. Possible commands:

            pywu current condition
            pywu current temp_f
            pywu current temp_c
            pywu current humidity
            pywu current icon
            pywu current wind
            pywu current pressure_mb
            pywu current pressure_in
            pywu current dewpoint_c
            pywu current dewpoint_f
            pywu current heat_index_c
            pywu current heat_index_f
            pywu current windchill_c
            pywu current windchill_f
            pywu current feelslike_c
            pywu current feelslike_f
            pywu current visibility_mi
            pywu current visibility_km
            pywu current prec_hour_in
            pywu current prec_hour_cm
            pywu current prec_day_in
            pywu current prec_day_cm


        forecast: Display forecast statistics. Possible commands:

            pywu forecast day
            pywu forecast shortdate
            pywu forecast longdate
            pywu forecast low_f
            pywu forecast low_c
            pywu forecast high_f
            pywu forecast high_c
            pywu forecast icon
            pywu forecast condition
            pywu forecast rain_in
            pywu forecast rain_mm
            pywu forecast snow_in
            pywu forecast snow_cm

            -d {0,1,2,3,4,5,6,7,8,9}, --day {0,1,2,3,4,5,6,7,8,9}
                Day to display forecast information from. Default is 0 (today).

                Example: pywu forecast condition --day 1


        info: Display forecast information. Possible commands:

            pywu info city
            pywu info postal
            pywu info datetime
            pywu info location
            pywu info country
            pywu info latitude
            pywu info longitude
            pywu info elevation
            pywu info observation


optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Display additional information (use this if you are expecting output but recieve none)

  -f <min>, --fetch <min>
                        Requires config file. Use to fetch new information before printing current/forecast condition if temporary file is older than given minutes (has no effect with `pywu fetch`)
```


### Conky

pywu can be used with Conky. An example conkyrc is provided in the examples directory. It's recommended to have a script call `pywu fetch` before conky starts and then periodcally from within the conkyrc (the example shows every 15 minutes or 900 seconds).
