# openpoiservice/server/parser.py
import os
import logging
import sqlalchemy
from flask_sqlalchemy.session import Session

from openpoiservice.server.db_import.models import POIs
from openpoiservice.server.db_import.parse_osm import OsmImporter
from openpoiservice.server.utils.decorators import timeit, processify
from openpoiservice.server import ops_settings, db
from imposm.parser import OSMParser
from collections import deque

logger = logging.getLogger(__name__)


# process this function to free memory after import of each osm file
@timeit
@processify
def parse_file(osm_file, osm_file_index=0, update_mode=False):
    logger.info(f"Starting to read {osm_file}")
    workers = ops_settings["concurrent_workers"]
    osm_importer = OsmImporter(osm_file_index, update_mode=update_mode)

    logger.info("Parsing and importing nodes...")
    OSMParser(concurrency=workers, nodes_callback=osm_importer.parse_nodes).parse(osm_file)
    if osm_importer.failed:
        logger.warning(f"Parsing {osm_file} failed due to an SQL error, likely caused by duplicate IDs. \n"
                       f"         The file has been marked to be imported later, run update after init completes.")
        del osm_importer
        return 1
    logger.info(f"Found {osm_importer.nodes_cnt} nodes")

    logger.info("Parsing relations...")
    OSMParser(concurrency=workers, relations_callback=osm_importer.parse_relations).parse(osm_file)

    logger.info(f"Found {osm_importer.relations_cnt} ways in relations")

    logger.info("Parsing ways...")
    OSMParser(concurrency=workers, ways_callback=osm_importer.parse_ways).parse(osm_file)
    logger.info(f"Found {osm_importer.ways_cnt} ways (including the ones found in relations)")

    # not needed any more after parsing ways
    del osm_importer.relation_ways

    # Sort the ways by the first osm_id reference, saves memory for parsing coordinates
    osm_importer.process_ways.sort(key=lambda x: x.refs[0])

    # speed optimization, see https://docs.python.org/3/library/collections.html#collections.deque
    osm_importer.process_ways = deque(osm_importer.process_ways)

    # note this will NOT work concurrently due to the algorithm for node id matching
    logger.info("Importing ways...")
    OSMParser(concurrency=1, coords_callback=osm_importer.parse_coords_for_ways).parse(osm_file)
    if osm_importer.failed:
        logger.warning(f"Parsing {osm_file} failed due to an SQL error, likely caused by duplicate IDs. \n"
                       f"         The file has been marked to be imported later, run update after init completes.")
        del osm_importer
        return 1

    if len(osm_importer.process_ways) > 0:
        logger.warning(f"{len(osm_importer.process_ways)} ways not processed due to missing coordinate information, "
                       f"possible pbf file corruption")

    # store remaining data in buffer
    osm_importer.save_buffer()

    logger.info(f"Found {osm_importer.pois_count} POIs")
    logger.info(f"Finished import of {osm_file}")
    del osm_importer
    return 0


@timeit
def run_import(osm_files_to_import, import_log):
    try:
        update_mode = False
        # run query on separate database connection, will conflict otherwise since parse_import runs in separate process
        with Session(db=db) as session:
            prev_poi_count = session.query(POIs.osm_type, POIs.osm_id).count()
            if prev_poi_count > 0:
                update_mode = True
                logger.info("Data import running in UPDATE MODE")
    except sqlalchemy.exc.ProgrammingError:
        logger.error("Database has not been initialized! Existing.")
        return

    for osm_file_index, osm_file in enumerate(osm_files_to_import):
        if osm_file in import_log and import_log[osm_file] == os.path.getmtime(osm_file):
            logger.info(f"File {osm_file} has not changed since last update, skipping")
            continue

        if update_mode:
            with Session(db=db) as session:
                prev_poi_count_file = session.query(POIs.osm_type, POIs.osm_id).filter_by(src_index=osm_file_index).count()
                logger.info(f"Setting flags on {prev_poi_count_file} POIs.")
                session.query(POIs).filter_by(src_index=osm_file_index).update({POIs.delflag: True})
                session.commit()

        if parse_file(osm_file, osm_file_index, update_mode=update_mode) == 0:
            import_log[osm_file] = os.path.getmtime(osm_file)
        else:
            import_log[osm_file] = 0  # import failed, this file has to be inserted in the next update

    if update_mode:
        delete_marked_entries()

    logger.info(f"Import complete.")


@timeit
def delete_marked_entries():
    logger.info(f"Updates complete, now performing delete operations...")
    with Session(db=db) as session:
        to_delete = session.query(POIs.osm_type, POIs.osm_id).filter_by(delflag=True).count()
        if to_delete > 0:
            logger.info(f"{to_delete} POIs in the database have been removed from the OSM data, deleting...")
            session.query(POIs).filter_by(delflag=True).delete()
            session.commit()
        else:
            logger.info(f"No POIs marked for deletion, nothing to do.")
