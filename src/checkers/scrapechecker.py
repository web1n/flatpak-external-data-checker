# Scrape Checker: A checker which finds the first link matching a pattern
# on some web page. For example, the latest URL for the standalone Flash Player
# Projector app can be found on a page of Adobe's website; the x-checker-data
# for the module looks like this (line-wrapped for legibility):
#
#   "x-checker-data": {
#       "type": "scrape",
#       "url": "https://www.adobe.com/support/flashplayer/debug_downloads.html",
#       "pattern": "https://fpdownload.macromedia.com/pub/flashplayer/updaters/
#                   (\\d+)/flash_player_sa_linux.x86_64.tar.gz"
#   }
#
# Copyright © 2019 Endless Mobile, Inc.
#
# Authors:
#       Rob McQueen <ramcq@endlessm.com>
#       Will Thompson <wjt@endlessm.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import bs4
import logging
import re

from lib.utils import get_url_contents, get_extra_data_info_from_url
from lib.externaldata import Checker, ExternalFile, ExternalData

log = logging.getLogger(__name__)


class ScrapeChecker(Checker):
    def _should_check(self, external_data):
        return external_data.checker_data.get("type") == "scrape"

    def check(self, external_data):
        if not self._should_check(external_data):
            return

        url = external_data.checker_data["url"]
        pattern = external_data.checker_data["pattern"]
        expr = re.compile(pattern)

        logging.debug("Searching for %s on %s", pattern, url)
        contents = get_url_contents(url)
        soup = bs4.BeautifulSoup(contents, "lxml")
        link = soup.find("a", href=lambda href: href and expr.match(href))

        if link:
            href = link.attrs["href"]
            new_url, checksum, size = get_extra_data_info_from_url(href)
            new_version = ExternalFile(new_url, checksum, size)
            if external_data.current_version.matches(new_version):
                external_data.state = ExternalData.State.VALID
            else:
                external_data.new_version = new_version
                if external_data.current_version.url == href:
                    external_data.state = ExternalData.State.BROKEN
                # otherwise, the existing url might in principle still work
        else:
            log.warning("No link matching %s found on %s", pattern, url)
            external_data.state = ExternalData.State.BROKEN
