from SubstanceInfoField import SubstanceField
from fhcrc_clinical.SocialHistories.DataLoading.DataLoadingGlobals import *


class SecondhandAmount(SubstanceField):
    __version__ = 'SubstanceInfo1.0'

    def __init__(self):
        SubstanceField.__init__(self)
        self.field_name = 'SecondhandAmount'
        self.table = SOC_HISTORIES
        self.substance = SECONDHAND
        self.field = AMOUNT
