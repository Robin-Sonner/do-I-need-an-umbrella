# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### [0.0.4] - 2026-02-08

### Added

- App: Settings UI, Weather Forecast UI
- WeatherForecastLite and WeatherForecast: temperature_mean, apparent_temperature_mean, precipitation_sum available as Daily Variables
- WeatherForecastLite and WeatherForecast: get_detailed_data method allowing for customized section length

### Changed

- Changed: Zooming in/out of the diagrams disabled in today's weather tab

### Fixed

- Fixed: Strings no longer cut off at the top and bottom


## [0.0.3] - 2026-02-05

### Fixed

- GitHub Action Pipeline now has write permission


## [0.0.2] - 2026-02-05

### Added

- Initial Application

### Changed

- Test Release of the library and app with the GitHub Actions Pipeline

### Fixed

- Daily Variables (temperature_min, temperature_max, precipitation_probability) 
  of DailyWeather and DailyWeatherLite are now set to their correct values, instead of always 0


## [0.0.1] - 2026-02-04

### Added

- Initial Library

### Changed

- Test Release of the library and app with the Jenkins Pipeline
