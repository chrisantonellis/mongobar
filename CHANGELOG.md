# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [ 0.0.8 ] 2017-09-21

### Added

* clean parser exit on 'backup not found'

### Changed

* fixed bug with removing a backup
* renamed 'hosts' action to 'dirs' to match 'connection directory' naming
* renamed get_hosts method to get_connection_directories in Mongobar class
* changed formatted connection name color from MAGENTA to YELLOW

## [ 0.0.7 ] 2017-09-18

### Added

* colored loglevels using Colorama for stream logging handler

### Changed

* main parser name adjusted
* setup.py description adjusted
* MongobarScript.capture_multiline_input fixed
* MongobarScript.capture_multiline_input exceptions captured correctly
* logger.warn calls changed to logger.warning due to deprecation notice from unittest
* fixed param name bug with calling restore
* fixed bug with determining destination connection on restore

## [ 0.0.6 ] 2017-09-06

### Added

* Connection.validate method
  * integrated into tests
  * integrated into Connections.add method
* updated test_mongobar tests to get to 100% coverage

## [ 0.0.5 ] 2017-09-06

### Added

* CHANGELOG.MD
* .travis.yml

### Changed

* version moved from __init__.py to __version__.py
* setup.py updated to use __version__.py
* tests updated to work in travis environment
* added badges to README.md

## [ 0.0.4 ] 2017-09-02

### Added
* initial release
