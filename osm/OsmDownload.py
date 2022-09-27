import os
import subprocess
from time import sleep
from urllib import parse

class OsmDownload():
    
    name = "geofabrik_spider"
    start_url = 'https://download.geofabrik.de'
    end_url = '-latest.osm.pbf'
    wait_time = 30

    #mapName: a path to a download link on geofabrik.de (download.geofabrik.de) like '/europe/germany/nordrhein-westfalen'
    def getMap(self, mapName):
        if (not mapName):
            print('Missing argument mapName')
            return

        if not mapName.startswith('/') : mapname = '/' + mapName # unneccessary?
        if mapName.endswith('/') : mapName = mapName.rstrip("/") 
        download_link =  parse.urljoin(self.start_url, mapName + self.end_url)
        print('Starting download of {}'.format(download_link))

        res = subprocess.call(["wget", "-q", "-N", download_link])
        print('End download with {}', res)


