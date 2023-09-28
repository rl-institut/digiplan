# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project tries to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- RES share charts and choropleth for user scenario
- Battery storages hook to esys model

### Changed
- Remove locale EN

### Fixed
- various fixes in charts, texts and units
- RES share calculation for SQ
- power and heat demand scaling for future scenario
- swap mapping of PV roof and PV ground in result calculation
- heat per capita calculation in results
- round chart values to decent fps
- diverging capacities in digipipe datapackage and app due to operational status

## [0.6.0] - 2023-09-01
### Added
- electricity autarky chart
- import and export to electricity overview chart
- heat chart overview
- tour explaining statusquo, settings and results
- selection to hide choropleth and region chart in SQ and 2045 dropdown
- results for heat overview chart
- results for GHG reduction chart
- adapt full load hours for renewables
- demand results for 2045 scenario
- onboarding charts

### Changed
- remove language button
- rework result charts
- rework top navigation and linked pages
- hide main charts in today and result section
- remove transport sector

### Fixed
- ghg reduction chart
- slider mark at wrong position
- reduce number of attributes in unit popups
- add missing German texts
- remove redundant sliders in settings
- add onboarding texts

## [0.5.0] - 2023-07-13
### Added
- heat settings set for oemof simulation
- cluster popups
- url, view and calculations for result charts
- datapackage from digipipe
- models, layers and legend items from digipipe geodata

### Changed
- legend layer colors and symbols
- static layer order
- paths for oemof hooks to digipipe scalars

### Fixed
- units
- tour shows up after onboarding

## [0.4.0] - 2023-06-20
### Added
- complete energy settings
- calculation for electricity overview chart
- calculation for heat overview chart
- function to create echart from options
- integration of celery for oemof simulations
- start oemof simulation
- oemof hooks for adapting RE capacities and electric demand

### Changed
- updated detailed overview chart
- deactivate choropleths when switching to settings tab
- switched to oemof.tabular postprocessing (instead of using oemoflex)
- removed legacy config
- moved schema examples to test folder
- moved map/chart view toggle to nav bar
- hide map/chart view toggle in status quo and settings menu

### Fixed
- info tooltips at settings
- chart tiles and results dropdown visible at same time
- chart view is closed when navigating to status quo or settings tab
- settings are translated

## [0.3.1] - 2023-03-30
### Added
- missing translations

### Changed
- removed unnecessary account and user stuff
- moved view toggle tabs to top right

## [0.3.0] - 2023-03-30
### Added
- first draft for demand preprocessing for oemof simulation
- preprocessing oemof build from user settings (#111) using hooks
- sentry in production
- intro tour using shepard.js
- language support
- goal charts to side panel
- user settings preprocessing for oemof simulation

### Changed
- move logos to top navbar

## [0.2.1] - 2023-03-27
### Fixed
- geopackage names and layer names

## [0.2.0] - 2023-03-27
### Added
- test coverage to dev setup
- CI with github actions (pre-commit and pytest)
- (static) charts for electricity and mobility
- dynamic choropleths
- popups from templates
- e-charts for detailed and ghg overview to charts panel
- layer switches to map legend
- legend for choropleths
- CONTRIBUTING.md file
- goal charts in sidebar as placeholders

### Changed
- integrated mapengine
- implementation of clustered layers
- move navigation buttons below top navbar

### Fixed
- choropleth and schema tests
- migration conflict
- data processing script

## [0.1.0] - 2023-02-10
### Added
- integrated django-oemof app
- add default schema, example, and tests
- switch to different tiling service, add satellite base map layer, and toggle controls #25
- enable basic popup on results layer
- results layer with customizable result views
- add names and lookups for layers
- add color palettes for map
- add category bbuttons to results side panel as placeholder

### Changed
- make dependent slider values update dynamically on dependency slider changes
- make creation of sidepanel menus programmatic
- update and add new icons
- update test API JSON and dependent JS implementation to reflect changes made in #77
- make data in legend dynamically and add legend schema and example
- extend popup schema with key values component
- load satellite layer beneath symbol layers #43
- switch top left logo for final version
- switch to Digiplan favicon set
- make JS imports programmatic and clean base and map html
- install patched custom django-raster version via pyproject.toml
- use modern (v2) node package lock format
- make local development without Docker possible out of the box
- removed users and admin apps
- change license to GNU AGPL v3
- make top nav responsive
- update horizontal padding on left panel for better use of bg-colors individual items
- colors for choropleth are rendered by colorbrewer
- make layers box visible on start

### Fixed
- fix clunky sidebar resizing of sidebar chart #68
- fix Postgis on Mac by improving Docker postgis install
- remove unneeded option flag in poetry install section in readme
- fix legend lower part hidden on smaller screens

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
