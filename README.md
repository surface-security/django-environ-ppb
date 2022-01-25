# django-environ

[django-environ](https://github.com/joke2k/django-environ) is the Python package that allows you to use [Twelve-factor methodology](http://www.12factor.net/) to configure your Django application with environment variables.

This is the PPB extension of it adding `_VAULT` and `_FILE` support to environment variable name parsing to read the setting from (respectivelly) that vault key or that file.

This should probably be a fork of the package instead of keeping it as a separate package.. TODO.


## Usage

Refer to [testapp](testapp) for a working example.

As in [testapp settings](testapp/testapp/settings.py), initialize environ:

```python
import ppbenviron

ENV_VAR = ppbenviron.CustomEnv()
ENV_VAR.read_env(BASE_DIR / 'local.env')

ENV_VAR.setup_vault(
    'ENVTEST_VAULT_URL',
    'ENVTEST_VAULT_TOKEN',
    'ENVTEST_VAULT_MOUNT',
    'ENVTEST_VAULT_PATHS',
    default_url='http://vault.local',
    default_token='tok3n',
    default_mount='/secrets',
    default_paths='staging,production',
)
```

Define settings:

```python
TEST_SETTING_STR = ENV_VAR('ENVTEST_STR', default='missed')
TEST_SETTING_LIST = ENV_VAR('ENVTEST_LIST', default=['missed'])
```

Create a `testapp/local.env` or define the environment variabls in the current shell:

```env
ENVTEST_VAULT_TOKEN_FILE=/home/myuser/.vault-token
ENVTEST_VAULT_MOUNT=other_mount
ENVTEST_VAULT_PATHS=dev,prd
```

`ENVTEST_STR_FILE=/path/to/file` will load `/path/to/file` in `TEST_SETTING_STR`.

`ENVTEST_STR_VAULT=somepath` will load `/other_mount/prd[somepath]` in `TEST_SETTING_STR` if it exists otherwise fallback to `/other_mount/qa[somepath]`

