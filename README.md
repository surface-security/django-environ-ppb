# django-environ

[django-environ](https://github.com/joke2k/django-environ) is the Python package that allows you to use [Twelve-factor methodology](http://www.12factor.net/) to configure your Django application with environment variables.

This is the PPB extension of it adding `_VAULT` and `_FILE` support to environment variable name parsing to read the setting from (respectivelly) that vault key or that file.

This should probably be a fork of the package instead of keeping it as a separate package.. TODO.


## TODO

* rename python package and classes (`ppbenviron` / `CustomEnv` ...?), or just fork and re-use that package name (`environ`)
