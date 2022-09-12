# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [SCOMPMX-2022r3] - 2022-09-12
### Added
- Support for the [MX3 Beamline library] via mxcubecore. This includes:
    - Testrig motors
    - Camera
    - Simulated Energy PV
- Support for driving Ophyd motors through the MCXuBE3 interface
- Display images from black-fly cameras in MXCuBE3
- Support for running bluesky plans
- `Raster` and `screen and collect` workflows
- Option to run mxcubecore in simulation mode
- Display a heatmap representing the number of spots in a grid for when a `raster` workflow is executed.

[SCOMPMX-2022r3]: https://confluence.synchrotron.org.au/confluence/display/SCOMPROJ/MX3+-+Releases+-+Project+Increment+1
[mx-simplon-api]: https://bitbucket.synchrotron.org.au/projects/MX3/repos/mx-sim-plon-api/browse
[MX3 Beamline library]: https://bitbucket.synchrotron.org.au/projects/MX3/repos/mx3-beamline-library/browse