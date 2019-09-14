#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

from __future__ import print_function

from importlib import import_module
import os.path
import pandas as pd
import unittest

from tests.common_functions import create_abstract_model, \
    add_components_and_load_data

TEST_DATA_DIRECTORY = \
    os.path.join(os.path.dirname(__file__), "..", "..", "test_data")

# No prerequisite modules
NAME_OF_MODULE_BEING_TESTED = "temporal.operations.timepoints"

try:
    MODULE_BEING_TESTED = import_module("." + NAME_OF_MODULE_BEING_TESTED,
                                        package='gridpath')
except ImportError:
    print("ERROR! Couldn't import module " + NAME_OF_MODULE_BEING_TESTED +
          " to test.")


class TestTimepoints(unittest.TestCase):
    """

    """
    def test_add_model_components(self):
        """
        Test that there are no errors when adding model components
        :return:
        """
        create_abstract_model(prereq_modules=[],
                              module_to_test=MODULE_BEING_TESTED,
                              test_data_dir=TEST_DATA_DIRECTORY,
                              subproblem="",
                              stage=""
                              )

    def test_load_model_data(self):
        """
        Test that data are loaded with no errors
        :return:
        """
        add_components_and_load_data(prereq_modules=[],
                                     module_to_test=MODULE_BEING_TESTED,
                                     test_data_dir=TEST_DATA_DIRECTORY,
                                     subproblem="",
                                     stage=""
                                     )

    def test_initialized_components(self):
        """
        Create components; check they are initialized with data as expected
        """

        # Load test data
        timepoints_df = \
            pd.read_csv(
                os.path.join(TEST_DATA_DIRECTORY, "inputs", "timepoints.tab"),
                sep="\t",
                usecols=['TIMEPOINTS', 'number_of_hours_in_timepoint', 'month']
            )

        m, data = \
            add_components_and_load_data(prereq_modules=[],
                                         module_to_test=MODULE_BEING_TESTED,
                                         test_data_dir=TEST_DATA_DIRECTORY,
                                         subproblem="",
                                         stage="")
        instance = m.create_instance(data)

        expected_tmp = timepoints_df['TIMEPOINTS'].tolist()
        actual_tmp = [tmp for tmp in instance.TIMEPOINTS]
        self.assertListEqual(expected_tmp, actual_tmp,
                             msg="TIMEPOINTS set data does not load correctly."
                             )

        expected_num_hrs_param = \
            timepoints_df.set_index('TIMEPOINTS').to_dict()[
                'number_of_hours_in_timepoint'
            ]
        actual_num_hrs_param = \
            {tmp: instance.number_of_hours_in_timepoint[tmp]
             for tmp in instance.TIMEPOINTS
             }
        self.assertDictEqual(expected_num_hrs_param, actual_num_hrs_param,
                             msg="Data for param "
                                 "'number_of_hours_in_timepoint'"
                                 " not loaded correctly")

        # Set: MONTHS
        self.assertListEqual([m for m in instance.MONTHS],
                             [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        # Param: month
        expected_month_param = \
            timepoints_df.set_index('TIMEPOINTS').to_dict()[
                'month'
            ]
        actual_month_param = \
            {tmp: instance.month[tmp]
             for tmp in instance.TIMEPOINTS
             }
        self.assertDictEqual(expected_month_param, actual_month_param,
                             msg="Data for param 'month' not loaded correctly")

        # TODO: we're missing a test for the loading of the
        #  previous_stage_timepoint_map param


if __name__ == "__main__":
    unittest.main()
