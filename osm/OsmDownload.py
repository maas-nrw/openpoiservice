import subprocess
from urllib import parse


class OsmDownload:
    name = "geofabrik_spider"
    start_url = 'https://download.geofabrik.de'
    end_url = '-latest.osm.pbf'
    wait_time = 30

    # mapName: a path to a download link on geofabrik.de (download.geofabrik.de) like '/europe/germany/nordrhein-westfalen'
    def get_map(self, map_name):
        if not map_name:
            print('Missing argument mapName')
            return

        if not map_name.startswith('/'):
            map_name = '/' + map_name  # unneccessary?
        if map_name.endswith('/'):
            map_name = map_name.rstrip("/")
        download_link = parse.urljoin(self.start_url, map_name + self.end_url)
        print('Starting download of {}'.format(download_link))

        res = subprocess.call(["wget", "-q", "-N", download_link])
        print(f'End download with {res}')
