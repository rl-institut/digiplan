# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project tries to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- switch to different tiling service, add satellite base map layer, and toggle controls #25
- enable basic popup on results layer
- results layer with customizable result views

### Changed
- make JS imports programmatic and clean base and map html
- install patched custom django-raster version via pyproject.toml
- use modern (v2) node package lock format
- make local development without Docker possible out of the box
- removed users and admin apps
- change license to GNU AGPL v3

### Fixed
- Fix Postgis on Mac by improving Docker postgis install
- remove unneeded option flag in poetry install section in readme

## [0.0.0] - 2022-06-30
### Added
- custom popup templates
- raster layers
- layers can be filtered by match of keywords
- layers can be filtered by multiple filters
- about page
- intro modal
- grid layer

### Changed
- exchanged mapbox with maplibre (open source)
- prevent zoom, if marker is clicked
- district and region filters are now global filters (not per layer)
- layer panel to accordion
- category order and labels
- regions are filtered in panel (not in search)

### Fixed
- district filter disabled
- undeclared variable error in JS (using strict mode)
- map grid only shown in debug mode
- stick footer to bottom
