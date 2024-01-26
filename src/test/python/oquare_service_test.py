
import unittest
#src/main/python/end_point/business/services/evaluation/oquare_service.py
from end_point.business.services.evaluation.oquare_service import OQuareMetrics
from end_point.business.cache.cache_db import CacheDB
#@build_json_from_cache(self, db_cache):

class TestOquareMetrics(unittest.TestCase):
    def setUp(self):
        self.db_cache = CacheDB()
        self.oquaremetrics = OQuareMetrics()
        self.test_base_path = "/home/lggarcia/euhubs4data-graph-wp5.2/oquareResult_BASE.xml"

    def test_oquare_endpoint(self):
        self.oquaremetrics = OQuareMetrics()
        self.oquaremetrics.read_file_to_cache(self.test_base_path, self.db_cache)
        json_build = self.oquaremetrics.build_json_from_cache(self.db_cache)
        self.assertIsNotNone(json_build)


if __name__ == "__main__":
    unittest.main()
