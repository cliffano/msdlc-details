<!-- BEGIN:AVATAR -->
To be populated by generator-python python-lib-partials
<!-- END:AVATAR -->

<!-- BEGIN:BADGES -->
To be populated by generator-python python-lib-partials
<!-- END:BADGES -->

# MSDLC Details

MSDLC Details is a Micro library for retrieving Microsoft Download Center page details .

## Installation

```shell
pip3 install msdlcdetails
```

## Usage

Create a configuration file, e.g. `msdlcdetails.yaml`:

```yaml
---
text: Hello World
```

Create msdlcdetails object and run it:

```python
from msdlcdetails import Display

display = Display(conf_files=['msdlcdetails.yaml'])
text = display.format(reverse=False, transformation='lower')
print(text)
```

## Configuration

These are the configuration properties that you can use with `msdlcdetails` CLI.
Some example configuration files are available on [examples](examples) folder.

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `text` | String | The message text | Hello World |

## Colophon

<!-- BEGIN:DEVELOPERS_GUIDE -->
To be populated by generator-python python-lib-partials
<!-- END:DEVELOPERS_GUIDE -->

<!-- BEGIN:BUILD_REPORTS -->
To be populated by generator-python python-lib-partials
<!-- END:BUILD_REPORTS -->
