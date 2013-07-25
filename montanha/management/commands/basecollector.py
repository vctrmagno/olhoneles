# -*- coding: utf-8 -*-
#
# Copyright (©) 2010-2013 Estêvão Samuel Procópio
# Copyright (©) 2010-2013 Gustavo Noronha Silva
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import urllib
from datetime import datetime
from urllib2 import urlopen, Request, URLError, HTTPError
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from montanha.models import *


class BaseCollector(object):
    def debug(self, message):
        if self.debug_enabled:
            print message

    def update_legislators(self):
        exception("Not implemented.")

    def update_data(self):
        for mandate in Mandate.objects.filter(date_start__year=self.mandate_start.year):
            if self.full_scan:
                for year in range(self.mandate_start.year, datetime.now().year + 1):
                    self.update_data_for_year(mandate, year)
            else:
                self.update_data_for_year(mandate, datetime.now().year)

    def update_data_for_year(self, mandate, year):
        self.debug("Updating data for year %d" % year)
        for month in range(1, 13):
            self.update_data_for_month(mandate, year, month)

    def retrieve_uri(self, uri, data={}, headers={}):
        resp = None

        while True:
            try:
                if data:
                    req = Request(uri, urllib.urlencode(data), headers)
                else:
                    req = Request(uri, headers=headers)
                resp = urlopen(req)
                break
            except HTTPError, e:
                if e.getcode() != 404:
                    raise HTTPError(e.url, e.code, e.msg, e.headers, e.fp)
            except URLError:
                print "Unable to retrieve %s; will try again in 10 seconds." % (uri)

            time.sleep(10)

        return self.post_process_uri(resp.read())

    def post_process_uri(self, contents):
        # Some sites are not in utf-8.
        try:
            contents = contents.decode('utf-8')
        except UnicodeDecodeError:
            try:
                contents = contents.decode('iso-8859-1')
            except Exception:
                pass

        return BeautifulSoup(contents)