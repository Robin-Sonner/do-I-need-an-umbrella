# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### [1.0.0] - 2026-02-12

### Added

- Mode Selector in the WeatherForecastTab allowing switching between different temperature data
- Added App Icon

### Changed

- Improved Documentation of the dinau package
- If the Location is changed in the SettingsUI, the change is validated there. If invalid, this leads to an early failure,
instead of the invalid location only being noticed later.
- Detailed Weather Information in the CurrentWeatherTab is sorted better

### Fixed

- Fixed legend of the temperature and precipitation chart being invisible
- Added missing seperator in WeatherClient.get_weather_forecast. Missing seperator led to corrupted requests to the open meteo API, preventing the forecast from being retrieved.
- Console is now hidden in the executable

### Note
- The API of the dinau package hasn't changed, so a major release isn't strictly needed. 
But with how much the App has changed and considering the jump from beta to stable, i consider a major release to be appropiate.

### [0.1.3] - 2026-02-12

### Changed

- Test Release through Jenkins. Console is now hidden in the executable

### [0.1.2] - 2026-02-12

### Changed

- Test Release through GitHub Actions (0.1.1 failed)

### [0.1.1] - 2026-02-12

### Changed

- Test Release through GitHub Actions. Console is now hidden in the executable


### [0.1.0] - 2026-02-08

### Added

- App: Settings UI, Weather Forecast UI
- WeatherForecastLite and WeatherForecast: temperature_mean, apparent_temperature_mean, precipitation_sum available as Daily Variables
- WeatherForecastLite and WeatherForecast: get_detailed_data method allowing for customized section length

### Changed

- Changed: Zooming in/out of the diagrams disabled in today's weather tab

### Fixed

- Fixed: Strings no longer cut off at the top and bottom

### [0.0.4] - 2026-02-08

## Changed

- Test Release through the new GitHub Actions Pipeline (Matrix Testing, Windows and Linux + multiple Python Versions)

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
