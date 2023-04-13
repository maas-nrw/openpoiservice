# manage.py
import json
import logging
import os
import sys
import unittest
from json import JSONDecodeError

import click
from flask.cli import FlaskGroup

from openpoiservice.server import create_app, db
from openpoiservice.server.db_import import parser
from osm.OsmDownload import OsmDownload

logging.basicConfig(
    level=logging.DEBUG if os.environ.get('OPS_DEBUG', False) else logging.INFO,
    format='%(levelname)-8s %(message)s',
)
logger = logging.getLogger(__name__)

app = create_app()
cli = FlaskGroup(create_app=create_app)

# File for logging files list and change dates
logfile = "import-log.json"


def clear_log():
    with open(logfile, "w") as f:
        f.write("{}\n")
        f.close()


@cli.command()
def test():
    """Runs the unit tests without test coverage."""
    clear_log()
    db.drop_all()

    tests = unittest.TestLoader().discover("openpoiservice/tests", pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        sys.exit(1)
    sys.exit(0)


@cli.command()
def create_db():
    """Creates the db tables."""
    db.create_all()
    clear_log()


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()
    clear_log()


@cli.command()
def import_data():
    """Imports osm pbf data to postgis."""

    osm_files = []
    osm_dir = os.getcwd() + "/osm"

    for dir_name, subdir_list, file_list in os.walk(osm_dir):
        if dir_name.endswith("__pycache__"):
            continue
        logger.info(f"Found directory: {dir_name}")
        for filename in file_list:
            if filename.endswith(".osm.pbf") or filename.endswith(".osm"):
                osm_files.append(os.path.join(dir_name, filename))
    osm_files.sort()

    import_log = {}
    if os.path.isfile(logfile):
        with open(logfile) as f:
            try:
                import_log = json.load(f)
            except JSONDecodeError:
                pass
            finally:
                f.close()

    # we have found previous data in the database, check if file list has changed which would require a full rebuild
    if len(import_log) and set(import_log.keys()) != set(osm_files):
        logger.error(f"File set has changed since last import, full rebuild required. Exiting.")
        return

    logger.info(f"Starting to import OSM data ({len(osm_files)} files in batch)")
    logger.debug(f"Files in import batch: {osm_files}")
    parser.run_import(osm_files, import_log)

    with open(logfile, "w") as f:
        json.dump(import_log, f, indent=4, sort_keys=True)
        f.close()

#https://www.codedisciples.in/flask-commands.html
#https://flask.palletsprojects.com/en/2.0.x/cli/
@cli.command()
@click.argument('mapname')  #arg name must be lower case!
def add_map(mapname):
    """Downloads a map from geofarik.de. mapname must be like '/europe/germany/nordrhein-westfalen'. '-latest.osm.pdf' gets appended automatically."""
    logger.info(f"add_map called with : {mapname}")
    osm_dir = os.getcwd() + "/osm"
    os.chdir(osm_dir)
    OsmDownload().get_map(mapname)
    logger.info("End add_map")

if __name__ == '__main__':
    cli()
