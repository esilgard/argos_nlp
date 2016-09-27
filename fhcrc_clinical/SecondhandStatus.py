from SubstanceInfoField import SubstanceField
from fhcrc_clinical.SocialHistories.DataLoading.DataLoadingGlobals import *


class SecondhandStatus(SubstanceField):
    __version__ = 'SubstanceInfo1.0'

    def __init__(self):
        SubstanceField.__init__(self)
        self.field_name = 'SecondhandStatus'
        self.table = SOC_HISTORIES
        self.substance = SECONDHAND
        self.field = STATUS
