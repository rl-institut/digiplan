# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project tries to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- custom popup templates
- raster layers
- layers can be filtered by match of keywords
- layers can be filtered by multiple filters

### Changed
- prevent zoom, if marker is clicked
- district and region filters are now global filters (not per layer)

### Fixed 
- district filter disabled
- undeclared variable error in JS (using strict mode)
