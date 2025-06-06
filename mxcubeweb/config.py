import logging
import os
import sys

import ruamel.yaml
from pydantic.v1 import (
    BaseModel,
    ValidationError,
)

from mxcubeweb.core.models.configmodels import (
    AppConfigModel,
    FlaskConfigModel,
    MXCUBEAppConfigModel,
    SSOConfigModel,
    UIPropertiesListModel,
)


class ConfigLoader:
    @staticmethod
    def load(path: str, schema: BaseModel):
        with open(os.path.join(path), encoding="utf-8") as f:
            config = ruamel.yaml.YAML().load(f.read())
            try:
                model = schema.parse_obj(config)
            except ValidationError:
                logging.getLogger("HWR").error(f"Validation error in {path}:")
                logging.getLogger("HWR").exception("")
                sys.exit(-1)

        return model


class Config:
    CONFIG_ROOT_PATH: str = ""

    flask: FlaskConfigModel
    app: MXCUBEAppConfigModel
    sso: SSOConfigModel

    def __init__(self, fpath):
        Config.CONFIG_ROOT_PATH = fpath
        app_config = self.load_config("server", AppConfigModel)
        uiprop = self.load_config("ui", UIPropertiesListModel)

        self.flask = app_config.server
        self.app = app_config.mxcube
        self.app.ui_properties = uiprop
        self.sso = app_config.sso

    def load_config(self, component_name, schema):
        fpath = os.path.join(Config.CONFIG_ROOT_PATH, f"{component_name}.yaml")
        config = ConfigLoader().load(path=fpath, schema=schema)

        return config
