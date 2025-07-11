# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
## [2.2.3] - 2025-08-14

### Changed

- Improved accuracy of create_tree_stem_profile

## [2.2.2] - 2025-08-14

### Changed

- Several typing improvements

## [2.2.1] - 2025-08-14

### Changed

- Modified pylint and mypy configurations to better suit the project

### Fixed

- Multiple fixes and cleanups based on pylint and mypy findings

## [2.2.0] - 2025-08-12

### Added

- Metsi_grow implementation. #MELA2-51

## [2.1.2] - 2025-07-03

### Fixed

- Several typing related fixes and general cleanup

### Changed

- Vector data model moved into its own module
- Vectorized data no longer automatically overwrites previous data

## [2.1.1] - 2025-06-27

### Fixed

- Deletes old target files before creating new ones. #MELA2-48

## [2.1.0] - 2025-06-24

### Added

- Added 'vectorize' pre-processing operation
- Added 'npy' and 'npz' export_prepro options

## [2.0.4] - 2025-06-23

### Changed

- Updated project dependencies to work with Python 3.13
- Removed older versions of Python and R from pipeline matrix, added Python 3.13.5 and R 4.5.0

## [2.0.3] - 2025-06-23

### Changed

- Removed scipy and pyyaml from dependencies
- Moved Robot Framework dependency under tests

## [2.0.2] - 2025-06-18

### Added

- Implemented partial file simulation #MELA2-45
- Added Robot test SMK_02_partial 

## [2.0.1] - 2025-06-16

### Changed

- Perf: Improved export speed with grouping query #MELA2-44
- Perf: Improved speed and memory with EventTree class internal changes

## [2.0.0] - 2025-06-13

### Changed

- Control structure now contains direct function references instead of lookup strings for generators and operations

## [1.2.4] - 2025-06-12

### Added

- Added Robot tests environment and first Robot test SMK_01 #MELA2-42

## [1.2.3] - 2025-06-11

### Added

- Unit testing reports now published by Github workflow

## [1.2.2] - 2025-06-09

### Added

- Added changelog

### Fixed

- Changed project version in pyproject.toml to match tags and releases
