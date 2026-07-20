# Fake Devices Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![Downloads][download-latest-shield]]()
[![HACS Installs][hacs-installs-shield]]()
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

This integration creates fake devices in Home Assistant, useful for adding helper integrations like [Battery Notes](https://github.com/andrew-codechimp/ha-battery-notes) to real world non-smart devices that are not in Home Assistant, for example TV Remotes and Wall Clocks.

You can add the device name, manufacturer, model and serial number, plus model id, hardware, firmware and a URL as optional advanced fields. You can use these to store any short piece of text you want.

No entities are created, it's just a device placeholder for using with helpers where you have the option to add to a device.

_Please :star: this repo if you find it useful_

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/codechimp)


![Device Creation](https://raw.githubusercontent.com/andrew-codechimp/HA-Fake-Devices/main/images/configuration.png "Device Creation")

## Installation

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=andrew-codechimp&repository=HA-Fake-Devices&category=Integration)

Or search for Fake Devices via HACS.

[commits-shield]: https://img.shields.io/github/commit-activity/y/andrew-codechimp/HA-Fake-Devices.svg?style=for-the-badge
[commits]: https://github.com/andrew-codechimp/HA-Fake-Devices/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[exampleimg]: example.png
[license-shield]: https://img.shields.io/github/license/andrew-codechimp/HA-Fake-Devices.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/andrew-codechimp/HA-Fake-Devices.svg?style=for-the-badge
[releases]: https://github.com/andrew-codechimp/HA-Fake-Devices/releases
[download-latest-shield]: https://img.shields.io/github/downloads/andrew-codechimp/HA-Fake-Devices/latest/total?style=for-the-badge
[hacs-installs-shield]: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Flauwbier.nl%2Fhacs%2Ffake_devices&style=for-the-badge
