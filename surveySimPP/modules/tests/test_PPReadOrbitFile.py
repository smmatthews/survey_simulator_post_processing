#!/bin/python

import pytest
import pandas as pd

from ..PPReadOrbitFile import PPReadOrbitFile


def test_PPReadOrbitFile():
     
     rescol=10
     
     padafr=PPReadOrbitFile('./data/test/testorb.des', 0, 14, "whitespace")
     val=len(padafr.columns)
     
     assert rescol==val
     
     return
     