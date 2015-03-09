# -*- coding: utf-8 -*-
from .base import BW2DataTest
from .config import ConfigTest
from .data_store import DataStoreTestCase
from .database import DatabaseTest, SingleFileDatabaseTest
from .geo import GeoTest
from .ia import IADSTest, MethodTest, WeightingTest, NormalizationTest
from .json_database import JSONDatabaseTest, SynchronousJSONDictTest
from .query import QueryTest, FilterTest, ResultTest
from .search import SearchTest
from .serialization import JsonSantizierTestCase
from .updates import UpdatesTest
from .utils import UtilsTest, UncertainifyTestCase
from .validation import ValidationTestCase
