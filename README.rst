pywu
====

pywu is a simple python script for fetching data from Weather
Underground's API. You need an API key to use the script (get it
`here <http://www.wunderground.com/weather/api/>`__).


Installation
------------

pywu is available on `PyPI <https://pypi.python.org/pypi/pywu/>`__. You can
install it with pip:

::

    pip3 install pywu

If installing from source run:

::

    python3 setup.py build install


Usage
-----

::

    pywu [-h] [-v] [-f <min>] {fetch,current,forecast,info} ...

You must first fetch the data using the fetch command. This stores a
file in /tmp that contains the data. All other commands (current,
forecast, and info) read from this file.

fetch
~~~~~

Pull weather data from server. Use the format '<API key> <city>,<state>'
or simply your API key and zip code.

::

    pywu fetch <apikey> 'New York,NY'
    pywu fetch <apikey> 10001

You can also specify a language (the default is English). For example:

::

    pywu fetch <apikey> <location> FR

A list of possible language codes can be found
`here <http://www.wunderground.com/weather/api/d/docs?d=language-support>`__.

Instead of the above, you may also use a ~/.pywu.conf file and simply
call ``pywu fetch``. See below for more information.

current
~~~~~~~

Display current statistics. Possible commands:

::

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

forecast
~~~~~~~~

Display forecast statistics. Possible commands:

::

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

You can also specify a day:

::

    -d {0,1,2,3,4,5,6,7,8,9}, --day {0,1,2,3,4,5,6,7,8,9}

Default is 0 (today).

Example:

::

    pywu forecast condition --day 1

info
~~~~

Display forecast information. Possible commands:

::

    pywu info city
    pywu info postal
    pywu info datetime
    pywu info location
    pywu info country
    pywu info latitude
    pywu info longitude
    pywu info elevation
    pywu info observation

Verbose Output
~~~~~~~~~~~~~~

pywu is designed to stay quiet instead of print information or errors.
This is so these messages will not appear when used with Conky. To
override this, specify the -v parameter:

::

    pywu -v fetch

Fetching Inline
~~~~~~~~~~~~~~~

This requires a config file at ~/.pywu.conf. You can also fetch new
information at the same time as you print current/forecast information:

::

    pywu --fetch <min> current condition
    pywu -f <min> forecast condition -d 3

pywu will fetch new information if the current information is older than <min>.


Config file
-----------

pywu supports reading from a config file as well as passing your API
key/location via command line. A sample configuration:

~/.pywu.conf:

::

    [PYWU]
    apikey=<yourapikey>
    location=New York City, NY

You can also specify a language within the config file:

::

    [PYWU]
    ...
    language=FR


Conky
-----

pywu can be used with Conky. An example conkyrc is provided in the
examples directory. It's recommended to have a script call
``pywu fetch`` before conky starts and then periodcally from within the
conkyrc (the example shows every 15 minutes or 900 seconds).
