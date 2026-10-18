#define DiagHalReturnToFirmware Entry503Return
#include "entry498.S"
#undef DiagHalReturnToFirmware
.set entry498_continue, entry503_complete
#include "indicator.S"
