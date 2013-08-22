# -*- coding: utf-8 -*-
import codecs
import datetime
import time
from operator import attrgetter

from pyquery import PyQuery as pq
from jinja2 import Environment, FileSystemLoader


class Track(object):
    def __init__(self, artist, title, ts):
        self.artist = artist
        self.title = title
        self.date = datetime.datetime.fromtimestamp(float(ts))
        self.ts = ts


class NovaScrapper(object):

    url = 'http://www.novaplanet.com/radionova/cetaitquoicetitre/%s'

    def __init__(self, start, end):
        self.tracks = {}  # Let's store data indexed by their timestamp

        # Alter start because the nova page will give us too much info
        # otherwise.
        start = start + datetime.timedelta(minutes=50)
        self.scrap_page(start)

        while self.max_date < end:
            start = self.max_date + datetime.timedelta(minutes=50)
            self.scrap_page(start)

    @property
    def max_date(self):
        return datetime.datetime.fromtimestamp(self.max_ts)

    @property
    def max_ts(self):
        return float(max(self.tracks.keys()))

    def scrap_page(self, date):
        """Scrap a page, put the results in the self.collection attribute.

        Return the latest timestamp it parsed (as in the most recent) so that
        the scrapping can continue.
        """
        timestamp = time.mktime(date.timetuple())

        d = pq(url=self.url % timestamp)
        for item in d.find('.cestquoicetitre_results>div').items():
            artist = item('.artiste a').text()
            if artist is None:
                artist = item('.artiste').text()

            title = item('.titre').text()
            ts_class = (item('.time').parent().parent()[0]
                        .attrib['class'].split()[0])
            ts = ts_class.split('_')[-1]

            if ts not in self.tracks:
                self.tracks[ts] = Track(artist=artist, title=title, ts=ts)


def render_tracks(date, tracks):
    loader = FileSystemLoader('.')
    env = Environment(loader=loader)
    template = env.get_template('tracks.html')
    output = template.render(date=date, tracks=tracks)

    filename = '%s.html' % date.strftime('%Y-%m-%d')

    with codecs.open(filename, 'w+', encoding='utf-8') as f:
        f.write(output)


def parse_nova_lanuit():

    now = datetime.datetime.now()
    start = datetime.datetime(year=now.year, month=now.month,
                              day=now.day, hour=0, minute=00)

    end = datetime.datetime(year=now.year, month=now.month, day=now.day,
                            hour=6, minute=0)

    scrapper = NovaScrapper(start, end)

    tracks = scrapper.tracks.values()
    tracks.sort(key=attrgetter('date'))

    render_tracks(start, tracks)

if __name__ == '__main__':
    parse_nova_lanuit()