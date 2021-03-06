import json
import logging

import environ

logger = logging.getLogger(__name__)

try:
    import hvac

    _VAULT_CHECK = True
except ImportError:
    _VAULT_CHECK = False


class CustomEnv(environ.Env):
    vault_url = None
    vault_cache = None
    vault_token = None
    vault_mount = None
    vault_paths = None
    cache_file = None

    def setup_vault(
        self,
        url_var,
        token_var,
        mount_var,
        paths_var,
        default_url=environ.Env.NOTSET,
        default_token=environ.Env.NOTSET,
        default_mount=environ.Env.NOTSET,
        default_paths=environ.Env.NOTSET,
        persist_cache_var=environ.Env.NOTSET,
    ):
        self.vault_url = self.get_value(url_var, default=default_url)
        self.vault_token = self.get_value(token_var, default=default_token)
        self.vault_mount = self.get_value(mount_var, default=default_mount)
        self.vault_paths = self.list(paths_var, default=default_paths)
        if persist_cache_var != environ.Env.NOTSET:
            self.cache_file = self.get_value(persist_cache_var, default=None)
        if self.cache_file:
            try:
                with open(self.cache_file) as f:
                    data = f.read()
                # no need to throw JSONDecodeError on empty file
                if data.strip():
                    self.vault_cache = json.loads(data)
            except FileNotFoundError:
                # probably not cached yet, it is ok
                pass
            except Exception:
                logger.exception("Could not load Vault cache")

    def get_value(self, var, cast=None, default=environ.Env.NOTSET, parse_default=False):
        if var not in self.ENVIRON:
            tvar = '%s_FILE' % var
            if tvar in self.ENVIRON:
                value = super(CustomEnv, self).get_value(tvar)
                # let it break if invalid file, no default applies to _FILE
                with open(value) as f:
                    return self.parse_value(f.read(), cast)

            tvar = '%s_VAULT' % var
            if tvar in self.ENVIRON and _VAULT_CHECK and self.vault_token:
                value = super(CustomEnv, self).get_value(tvar)
                if self.vault_cache is None:
                    client = hvac.Client(url=self.vault_url, token=self.vault_token)
                    self.vault_cache = {}
                    for _p in self.vault_paths:
                        _k = '%s/%s' % (self.vault_mount, _p)
                        _v = client.read(_k)
                        if _v is None:
                            logger.error('Could not read %s from vault, ignoring', _k)
                        else:
                            self.vault_cache.update(_v['data'])
                    if self.cache_file is not None:
                        with open(self.cache_file, 'w') as f:
                            json.dump(self.vault_cache, f)

                if value in self.vault_cache:
                    return self.parse_value(self.vault_cache[value], cast)
                else:
                    logger.error('Could not find %s in Vault cache, returning default', value)

        # even if var no in ENVIRON, call super to handle defaulting...
        return super(CustomEnv, self).get_value(var, cast, default, parse_default)

    def bytes(self, var, default=environ.Env.NOTSET, encoding='utf8') -> bytes:
        return self.get_value(var, cast=str, default=default).encode(encoding)

    def str(self, var, default=environ.Env.NOTSET, multiline=False, must_end_with=None):
        value = super().str(var, default=default, multiline=multiline)
        if value is None or must_end_with is None:
            return value

        assert len(must_end_with) == 1

        if value[-1] == must_end_with:
            return value
        return value + must_end_with
