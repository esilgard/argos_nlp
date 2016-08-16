from SubstanceInfoField import SubstanceField
from fhcrc_clinical.SocialHistories.DataLoading.DataLoadingGlobals import *
from fhcrc_clinical.KeywordSearch.KeywordGlobals import *


class AlcoholQuitAge(SubstanceField):
    __version__ = 'SubstanceInfo1.0'

    def __init__(self):
        SubstanceField.__init__(self)
        self.field_name = 'AlcoholQuitAge'
        self.table = SOC_HISTORIES
        self.substance = ALCOHOL
        self.field = QUIT_AGE
