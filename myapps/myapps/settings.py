from myapps import apps
from myapps import constants


apps.Gridss().patch_application_settings(
        **{
            "config": constants.GRIDSS_CONFIG,
        }
)
