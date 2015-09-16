###
#
# Copyright (c) 2014, Dan Hasting
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the organization nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###

import argparse
from argparse import RawTextHelpFormatter

from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import quote

import configparser, sys, json, re, os, time


temp_file = "/tmp/pywu.cache.json"
conf_file = "~/.pywu.conf"



class OptionParser:

    parser = argparse.ArgumentParser(description="pywu pulls weather data from Weather "
        + "Underground's API.\n\nYou must first fetch the data using the fetch command. "
        + "This stores a file in /tmp that contains the data. All other commands (current, "
        + "forecast, and info) read from this file.\n\nFor more information, visit: "
        + "https://www.github.com/dh4/pywu\n\n"
        + "You can also pass the -h parameter to positional arguments. For example:\n    "
        + "pywu fetch -h", formatter_class=RawTextHelpFormatter)


    def __init__(self):

        # Verbose output option. All non-argparse error messages are suppressed (to prevent funky
        # output in conky if an error is raised). Using this flag allows the user to see that
        # error output.
        self.parser.add_argument("-v","--verbose", action="store_true", dest="verbose",
                                 default=False, help="Display additional information (use this "
                                 + "if you are expecting output but recieve none)\n\n")

        # The fetch argument allows a user to fetch new information while calling current, etc.
        self.parser.add_argument("-f","--fetch", action="store", dest="fetch", metavar="<min>",
                                 type=int, default=-1, help="Requires config file. Use to fetch "
                                 + "new information before printing current/forecast condition if "
                                 + "temporary file is older than given minutes (has no effect "
                                 + "with `pywu fetch`)\n\n")

        # We are going to use sub commands to make user input look cleaner
        subparser = self.parser.add_subparsers(dest="sub")

        # The fetch sub command. Used to populate the data file
        fetch_parser = subparser.add_parser("fetch")
        fetch_parser.add_argument("apikey", action="store", metavar="<apikey>", nargs="?",
                                  help="Fetch data with given API key\n\n")
        fetch_parser.add_argument("location", action="store", metavar="<location>", nargs="?",
                                  help="Fetch data with given location\n\n")
        fetch_parser.add_argument("language", action="store", metavar="<language>", nargs="?",
                                  help="Fetch data in the given language\n\n")

        # The current sub command. Used to fetch current conditions from the data file
        current_parser = subparser.add_parser("current")
        current_parser.add_argument("current",
            choices=["condition","temp_f","temp_c","humidity",
                     "icon","wind","pressure_mb","pressure_in","dewpoint_c","dewpoint_f",
                     "heat_index_c","heat_index_f","windchill_c","windchill_f","feelslike_c",
                     "feelslike_f","visibility_mi","visibility_km","prec_hour_in","prec_hour_cm",
                     "prec_day_in","prec_day_cm"],
            action="store", help="Display current statistic\nSee -h for possible values.\n\n")

        # The forecast sub command. Used to fetch future predictions from the data file.
        forecast_parser = subparser.add_parser("forecast")
        forecast_parser.add_argument("forecast",
            choices=["day","shortdate","longdate","low_f","low_c","high_f","high_c","icon",
                     "condition","rain_in","rain_mm","snow_in","snow_cm"],
            action="store", help="Display forecast statistic\nSee -h for possible values.\n\n")
        forecast_parser.add_argument("-d","--day", choices=[0,1,2,3,4,5,6,7,8,9], action="store",
            dest="day", default=0, type=int, help="Day to display forecast information from. "
            + "Default is 0 (today).\n\n")

        # The info sub command prints various information about the data feed.
        info_parser = subparser.add_parser("info")
        info_parser.add_argument("information",
            choices=["city","postal","datetime","location","country","latitude","longitude",
                     "elevation","observation"],
            action="store", help="Display forecast information\nSee -h for possible values.\n\n")


    def parse_args(self):
        args = self.parser.parse_args()
        return args

    def print_usage(self):
        self.parser.print_usage()



class ForecastData:

    data = None
    args = None
    verbose = False


    def __init__(self, args):

        self.args = args
        self.verbose = self.args.verbose;

        # Get values from config file
        conf = True
        config = configparser.ConfigParser()
        config.read(os.path.expanduser(conf_file))

        try:
            conf_key = config['PYWU']['apikey']
            conf_loc = config['PYWU']['location']
        except KeyError:
            conf = False

        if conf:
            try:
                conf_lang = config['PYWU']['language']
            except KeyError:
                conf_lang = 'EN'

        if args.sub == "fetch":
            apikey = args.apikey
            location = args.location
            language = args.language

            if language is None:
                language = 'EN'

            # If arguments not provided, use config values
            if apikey == None or location == None:
                if self.verbose: print("API key and location not found in arguments, "
                                 + "trying ~/.pywu.conf", file=sys.stdout)
                if conf and conf_key != "" and conf_loc != "":
                    apikey = conf_key
                    location = conf_loc
                    language = conf_lang
                else:
                    if self.verbose: print("Please provide an API key and location in ~/.pywu.conf",
                                     file=sys.stderr)
                    sys.exit(4)

            self.fetch_data(apikey, location, language)

        # If user passed --fetch, check for config file and update cache
        elif self.args.fetch > -1 and self.args.sub != None:
            if conf and conf_key != "" and conf_loc != "":
                age = time.time() - os.path.getmtime(temp_file)

                if age > self.args.fetch * 60:
                    if self.verbose: print("Updating cache file", file=sys.stdout)
                    self.fetch_data(conf_key, conf_loc, conf_lang)
                else:
                    if self.verbose: print("Cache file " + str(int(age / 60)) + " minutes old. "
                                     + "Not updating", file=sys.stdout)
            else:
                if self.verbose: print("Config file required to use --fetch", file=sys.stderr)

        try:
            f = open(temp_file, "r")
        except IOError:
            self.fetch_error()

        self.data = json.load(f)
        f.close()


    def fetch_data(self, apikey, location, language):

        # Grab data from Weather Underground API
        req = ("http://api.wunderground.com/api/%s/conditions/forecast10day/lang:%s/q/%s.json"
               % (apikey, language, quote(location)))

        if self.verbose: print("Fetching weather data...", file=sys.stdout)

        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason') and self.verbose:
                print(e.reason, file=sys.stderr)
            elif hasattr(e, 'code') and self.verbose:
                print("Status returned: " + str(e.code), file=sys.stderr)
            sys.exit(2)

        json_data = response.read().decode()
        data = json.loads(json_data)

        try:
            print(data['response']['error']['description'], file=sys.stdout)
            sys.exit(3)
        except KeyError:
            pass

        f = open(temp_file, "w")
        f.write(json_data)
        f.close()

        if self.verbose: print("Data fetched successfully", file=sys.stdout)


    def read_current(self):

        # Assign current conditions to a dictionary
        try:
            current = self.data['current_observation']
        except KeyError:
            self.fetch_error()

        # Collect and merge wind data
        wind_dir = current['wind_dir']
        wind_mph = current['wind_mph']
        wind = wind_dir + " " + str(int(round(float(wind_mph)))) + "mph"

        current_dict = {
            "condition"    : current['weather'],
            "temp_f"       : int(round(float(current['temp_f']))),
            "temp_c"       : int(round(float(current['temp_c']))),
            "humidity"     : current['relative_humidity'],
            "icon"         : self.convert_icon(current['icon'],True),
            "wind"         : wind,
            "pressure_mb"  : current['pressure_mb'],
            "pressure_in"  : current['pressure_in'],
            "dewpoint_c"   : current['dewpoint_c'],
            "dewpoint_f"   : current['dewpoint_f'],
            "heat_index_c" : current['heat_index_c'],
            "heat_index_f" : current['heat_index_f'],
            "windchill_c"  : current['windchill_c'],
            "windchill_f"  : current['windchill_f'],
            "feelslike_c"  : current['feelslike_c'],
            "feelslike_f"  : current['feelslike_f'],
            "visibility_mi": current['visibility_mi'],
            "visibility_km": current['visibility_km'],
            "prec_hour_in" : current['precip_1hr_in'],
            "prec_hour_cm" : current['precip_1hr_metric'],
            "prec_day_in"  : current['precip_today_in'],
            "prec_day_cm"  : current['precip_today_metric'],
        }

        return current_dict


    def read_forecast(self):

        # Assign forecast to a dictionary
        forecast_dict = []

        try:
            forecast = self.data['forecast']['simpleforecast']['forecastday']
        except KeyError:
            self.fetch_error()

        count = 1

        for index, node in enumerate(forecast):

            d = node['date']

            conditions = {
                "day"       : d['weekday'],
                "shortdate" : str(d['month']) + "/" + str(d['day']) + "/" + str(d['year']),
                "longdate"  : d['monthname'] + " " + str(d['day']) + ", " + str(d['year']),
                "low_f"     : node['low']['fahrenheit'],
                "low_c"     : node['low']['celsius'],
                "high_f"    : node['high']['fahrenheit'],
                "high_c"    : node['high']['celsius'],
                "icon"      : self.convert_icon(node['icon']),
                "condition" : node['conditions'],
                "rain_in"   : node['qpf_allday']['in'],
                "rain_mm"   : node['qpf_allday']['mm'],
                "snow_in"   : node['snow_allday']['in'],
                "snow_cm"   : node['snow_allday']['cm'],
            }

            forecast_dict.append(conditions)
            count += 1

        return forecast_dict


    def read_info(self):

        try:
            info = self.data['current_observation']
        except KeyError:
            self.fetch_error()

        info_dict = {
            "city"        : info['display_location']['city'],
            "postal"      : info['display_location']['zip'],
            "datetime"    : info['observation_time'],
            "location"    : info['display_location']['full'],
            "country"     : info['display_location']['country'],
            "latitude"    : info['display_location']['latitude'],
            "longitude"   : info['display_location']['longitude'],
            "elevation"   : info['display_location']['elevation'],
            "observation" : info['observation_location']['full'],
        }

        return info_dict


    def convert_icon(self, icon, current=False):

        pattern = re.compile(r'[A-Za-z]+ \d+ (.+):\d+:\d+')
        time_string = self.data['current_observation']['local_time_rfc822']
        hour = int(pattern.search(time_string).group(1))

        day_icon_dict = {
            "chancerain"    : "g",
            "sunny"         : "a",
            "mostlysunny"   : "b",
            "partlycloudy"  : "c",
            "mostlycloudy"  : "d",
            "rain"          : "i",
            "chancesnow"    : "o",
            "cloudy"        : "e",
            "tstorms"       : "m",
            "chancetstorms" : "k",
            "sleet"         : "q",
            "snow"          : "q",
            "fog"           : "e",
            "smoke"         : "e",
            "hazy"          : "e",
            "flurries"      : "p",
            "chanceflurries": "o",
            "chancesleet"   : "o",
            "clear"         : "a",
            "partlysunny"   : "c",
        }

        night_icon_dict = {
            "chancerain"    : "G",
            "sunny"         : "A",
            "mostlysunny"   : "B",
            "partlycloudy"  : "C",
            "mostlycloudy"  : "D",
            "rain"          : "i",
            "chancesnow"    : "O",
            "cloudy"        : "e",
            "tstorms"       : "m",
            "chancetstorms" : "K",
            "sleet"         : "q",
            "snow"          : "q",
            "fog"           : "e",
            "smoke"         : "e",
            "haze"          : "e",
            "flurries"      : "p",
            "chanceflurries": "o",
            "chancesleet"   : "o",
            "clear"         : "A",
            "partlysunny"   : "C",
        }

        try:
            if (hour > 20 or hour < 6) and current is True:
                new_icon = night_icon_dict[icon]
            else:
                new_icon = day_icon_dict[icon]
        except KeyError:
            if self.verbose: print("Icon type doesn't exist. Please report this.", file=sys.stderr)
            new_icon = ""

        return new_icon


    def fetch_error(self):

        e = "Data file has not been populated. Use 'pywu -v fetch <apikey> <location>' first."

        if self.verbose: print(e, file=sys.stderr)
        sys.exit(1)


    def output_data(self, parser):

        if self.args.sub == "current":
            current_dict = self.read_current()
            print(current_dict[self.args.current], file=sys.stdout)
        elif self.args.sub == "forecast":
            forecast_dict = self.read_forecast()
            print(forecast_dict[int(self.args.day)][self.args.forecast], file=sys.stdout)
        elif self.args.sub == "info":
            info_dict = self.read_info()
            print(info_dict[self.args.information], file=sys.stdout)
        elif self.args.sub != "fetch":
            parser.print_usage()



def main():

    parser = OptionParser()
    args = parser.parse_args()

    forecast = ForecastData(args)
    forecast.output_data(parser)


if __name__ == '__main__':

    main()
    sys.exit()
