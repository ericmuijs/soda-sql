#  Copyright 2020 Soda
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import json
import logging
import os
from typing import List
from unittest import TestCase

import yaml

from sodasql.profiles.profiles import Profile
from sodasql.scan.scan_configuration import ScanConfiguration
from sodasql.scan.scan_result import ScanResult
from tests.common.env_vars_helper import EnvVarsHelper
from tests.common.logging_helper import LoggingHelper
from sodasql.warehouse.warehouse import Warehouse


LoggingHelper.configure_for_test()


class SqlTestCase(TestCase):

    warehouse: Warehouse = None
    default_test_table_name = 'test_table'

    def __init__(self, method_name: str = ...) -> None:
        super().__init__(method_name)
        self.connection = None
        EnvVarsHelper.load_test_environment_properties()
        self.profile_name = os.getenv('SODA_TEST_PROFILE', 'test')
        self.profile_target_name = os.getenv('SODA_TEST_TARGET', 'local_postgres')

    def setUp(self) -> None:
        logging.debug(f'\n\n--- {str(self)} ---')
        super().setUp()
        warehouse_configuration = self.get_warehouse_configuration()
        if SqlTestCase.warehouse is not None \
                and SqlTestCase.warehouse.warehouse_configuration != warehouse_configuration:
            SqlTestCase.warehouse.close()
            SqlTestCase.warehouse = None
        if SqlTestCase.warehouse is None:
            SqlTestCase.warehouse = Warehouse(warehouse_configuration)
            SqlTestCase.warehouse.parse_logs.assert_no_warnings_or_errors('Test warehouse')
        self.warehouse = SqlTestCase.warehouse
        self.connection = self.warehouse.connection

    def get_warehouse_configuration(self):
        if self.profile_name == 'test' and self.profile_target_name == 'local_postgres':
            return {
                'name': 'test_postgres_warehouse',
                'type': 'postgres',
                'host': 'localhost',
                'port': '5432',
                'username': 'sodalite',
                'database': 'sodalite',
                'schema': 'public'}
        profile = Profile(self.profile_name, self.profile_target_name)
        if profile.parse_logs.has_warnings_or_errors() and 'No such file or directory' in profile.parse_logs.logs[0].message:
            logging.error(f'{Profile.USER_HOME_PROFILES_YAML_LOCATION} not found, creating default initial version...')
            initial_profile = {
                'test': {
                    'target': 'redshift',
                    'outputs': {
                        'redshift': {
                            'type': 'redshift',
                            'host': '***',
                            'port': '5439',
                            'username': '***',
                            'database': '***',
                            'schema': 'public'}
                        }}}
            with open(Profile.USER_HOME_PROFILES_YAML_LOCATION, 'w') as yaml_file:
                yaml.dump(initial_profile, yaml_file, default_flow_style=False)
            raise AssertionError(f'{Profile.USER_HOME_PROFILES_YAML_LOCATION} not found. '
                                 f'Default initial version was created. '
                                 f'Update credentials  for profile {self.profile_name}, '
                                 f'target {self.profile_target_name} in that file and retry.')
        profile.parse_logs.assert_no_warnings_or_errors(Profile.USER_HOME_PROFILES_YAML_LOCATION)
        return profile.properties

    def tearDown(self) -> None:
        self.connection.rollback()

    def sql_update(self, sql: str):
        assert self.connection, 'self.connection not initialized'
        cursor = self.connection.cursor()
        try:
            logging.debug(f'Test SQL update: {sql}')
            return cursor.execute(sql)
        finally:
            cursor.close()

    def sql_updates(self, sqls: List[str]):
        for sql in sqls:
            self.sql_update(sql)

    def create_table(self, table_name: str, columns: List[str], rows: List[str]):
        joined_columns = ", ".join(columns)
        joined_rows = ", ".join(rows)
        self.sql_updates([
            f"DROP TABLE IF EXISTS {table_name}",
            f"CREATE TABLE {table_name} ( {joined_columns} )",
            f"INSERT INTO {table_name} VALUES {joined_rows}"])

    def scan(self, scan_configuration_dict: dict) -> ScanResult:
        logging.debug('Scan configuration \n'+json.dumps(scan_configuration_dict, indent=2))

        scan_configuration: ScanConfiguration = ScanConfiguration(scan_configuration_dict)
        scan_configuration.parse_logs.assert_no_warnings_or_errors('Test scan')
        scan = self.warehouse.create_scan(scan_configuration)
        for log in scan.configuration.parse_logs.logs:
            logging.info(str(log))
        return scan.execute()

    def assertMeasurements(self, scan_result, column: str, expected_metrics_present):
        metrics_present = [measurement.metric for measurement in scan_result.measurements if measurement.column_name == column]
        self.assertEqual(set(metrics_present), set(expected_metrics_present))

    def assertMeasurementsPresent(self, scan_result, column: str, expected_metrics_present):
        metrics_present = [measurement.metric for measurement in scan_result.measurements if measurement.column_name == column]
        metrics_expected_and_not_present = [expected_metric for expected_metric in expected_metrics_present if expected_metric not in metrics_present]
        self.assertEqual(set(), set(metrics_expected_and_not_present))

    def assertMeasurementsAbsent(self, scan_result, column: str, expected_metrics_absent: list):
        metrics_present = [measurement.metric for measurement in scan_result.measurements if measurement.column_name == column]
        metrics_present_and_expected_absent = set(expected_metrics_absent) & set(metrics_present)
        self.assertEqual(set(), metrics_present_and_expected_absent)
