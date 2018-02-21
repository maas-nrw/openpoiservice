# openpoiservice/server/parser.py

from openpoiservice.server.db_import.parse_pbf import PbfImporter
from imposm.parser import OSMParser
from timeit import Timer


def run_import(path):
    pbf_importer = PbfImporter()

    osm_file_path = path

    relations = OSMParser(concurrency=4, relations_callback=pbf_importer.parse_relations)
    t = Timer(lambda: relations.parse(osm_file_path))
    print 'Time passed: {}s'.format(t.timeit(number=1))
    print 'Found {} ways in relations'.format(pbf_importer.relations_cnt)

    ways = OSMParser(concurrency=4, ways_callback=pbf_importer.parse_ways)
    t = Timer(lambda: ways.parse(osm_file_path))
    print 'Time passed: {}s'.format(t.timeit(number=1))
    print 'Found {} ways'.format(pbf_importer.ways_cnt)

    nodes = OSMParser(concurrency=4, nodes_callback=pbf_importer.parse_nodes)
    t = Timer(lambda: nodes.parse(osm_file_path))
    print 'Time passed to parse nodes: {}s'.format(t.timeit(number=1))

    coords = OSMParser(concurrency=4, coords_callback=pbf_importer.parse_coords)
    t = Timer(lambda: coords.parse(osm_file_path))
    print 'Time passed to parse coords for nodes from ways: {}s'.format(t.timeit(number=1))

    t = Timer(lambda: pbf_importer.parse_nodes_of_ways())
    print 'Time passed total: {}s'.format(t.timeit(number=1))
    print 'Found {} pois'.format(pbf_importer.pois_cnt)