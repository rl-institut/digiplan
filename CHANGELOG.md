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
- about page
- intro modal
- grid layer

### Changed
- prevent zoom, if marker is clicked
- district and region filters are now global filters (not per layer)
- layer panel to accordion
- category order and labels

### Fixed 
- district filter disabled
- undeclared variable error in JS (using strict mode)
- map grid only shown in debug mode
- stick footer to bottom
