# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Fixed

## [2.0.0b12] - 2021-02-16
### Changed
- Renamed CLI command init to analyze!
- (Internal refactoring) Extracted dataset analyzer

## [2.0.0b11] - 2021-02-16
### Changed
- Added missing table metadata queries for athena and bigquery (#97)

## [2.0.0b10] - 2021-02-11
### Changed
- Internal changes (token authorization)

## [2.0.0b9] - 2021-02-10
### Changed
- Internal changes (scan builder, authentication and API changes)

## [2.0.0b8] - 2021-02-08
### Changed
- Fixed init files
- Fixed scan logs

## [2.0.0b7] - 2021-02-06
### Changed
- Moved the SQL metrics inside the scan YAML files, with option to specify the SQL inline or refer to a file.
### Added
- Added column level SQL metrics
- Added documentation on SQL metric variables

## [2.0.0b6] - 2021-02-05
### Changed
- Upgrade library dependencies (dev-requirements.in) to their latest patch
- In scan.yml files, extracted metric categories from `metrics` into a separate `metric_groups` element

## [2.0.0b5] - 2021-02-01
### Changed
- Fixed Snowflake CLI issue

## [2.0.0b4] - 2021-02-01
### Changed
- Packaging issue solved which blocked CLI bootstrapping

## [2.0.0b3] - 2021-01-31
### Added
- Support for Snowflake
- Support for AWS Redshift
- Support for AWS Athena
- Support for GCP BigQuery
- Anonymous tests
### Changed
- Improved [docs on tests](https://docs.soda.io/soda-sql/documentation/tests.html)

## [2.0.0b2] - 2021-01-22
### Added
- Support for AWS PostgreSQL
### Changed
- Published [docs online](https://docs.soda.io/soda-sql/)

## [2.0.0b1] - 2021-01-15
Initial release
