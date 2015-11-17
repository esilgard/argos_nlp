#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import unittest
from mock import patch

import re
import PathStageT
import global_strings as dict_keys

EXPECTED_STAGE_NAME='PathStageT'
EXPECTED_REGEX='.*((pT|yT)[012345][abc]?).*'
EXPECTED_VERSION='PathStageT1.0'
EXPECTED_CONFIDENCE='0.98'

FULL_TEXT='Diagnosis: Murder'

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(PathStageTHappyCase)
    return suite

def run_tests():
    runner = unittest.TextTestRunner(verbosity = 2)
    runner.run(suite())

class PathStageTHappyCase(unittest.TestCase):

    def setUp(self):
        self.path_stage_t = PathStageT.PathStageT()

    def make_default_dictionary(self):
        ret = {}
        ret[(-1,'FullText',0,None)] = FULL_TEXT
        return ret

    def make_re_match_object(self):
        return re.match('*',FULL_TEXT,re.DOTALL)



    def test_init_happy_case(self):
        self.assertEqual(self.path_stage_t.stage_name, EXPECTED_STAGE_NAME)
        self.assertEqual(self.path_stage_t.regex, EXPECTED_REGEX)
        self.assertEqual(self.path_stage_t.return_dictionary, {})
        
    def test_get_version_happy_case(self):
        self.assertEqual(self.path_stage_t.get_version(), EXPECTED_VERSION)

    @patch('re.match')
    def test_get_happy_case(self, mock_match):
        disease_group='Cooties'
        dictionary=self.make_default_dictionary()

        re_match =  self.make_re_match_object()
        mock_match.match.return_value = re_match
        
        return_dictionary = self.path_stage_t.get(disease_group, dictionary)
        
        
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.NAME],EXPECTED_STAGE_NAME)
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.CONFIDENCE], EXPECTED_CONFIDENCE)
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.VERSION], EXPECTED_VERSION)
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.TABLE], dict_keys.STAGE_GRADE_TABLE)
        
        mock_match.assert_called_with(self.path_stage_t.regex, FULL_TEXT, re.DOTALL)
        
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.VALUE], re_match.group(1))
       

    @patch('re.match')
    def test_get_no_stage(self, mock_match):
        disease_group='Cooties'
        dictionary=self.make_default_dictionary()
        expected_dictionary = []
        mock_match.return_value = None
        
        return_dictionary = self.path_stage_t.get(disease_group, dictionary)
      
        
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.NAME],EXPECTED_STAGE_NAME)
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.CONFIDENCE], 0.0)
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.VERSION], EXPECTED_VERSION)
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.TABLE], dict_keys.STAGE_GRADE_TABLE)
        
        mock_match.assert_called_with(self.path_stage_t.regex, FULL_TEXT, re.DOTALL)

        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.VALUE], None)
        self.assertEqual(self.path_stage_t.return_dictionary[dict_keys.STARTSTOPS], []) 

if __name__ == '__main__':
    unittest.main()
