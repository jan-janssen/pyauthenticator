# Summary
The rest of the implementation is the user interface and the creation of the configuration file:
* `_cmd.py` - Command line interface, the main function is the `command_line_parser()` function.
* `_config.py` - JSON based configuration file interface with an `load_config()` function and an `write_config()` function.
* `_core.py` - Core functionality discussed previously
* `_user.py` - Python based user interface
* `_version.py` - Version of the software defined using [hatch-vcs](https://github.com/ofek/hatch-vcs).
* `api.py` - Programmatic interface 