from myapps import apps
from myapps import constants

apps.BwaMemGRCh38().patch_application_settings(
        **{
            "reference": constants.GRCH38_FASTA,
            "cores": {"WG": 32, "WE": 32, "TD": 4},
        }
)