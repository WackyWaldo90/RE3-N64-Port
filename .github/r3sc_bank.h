#ifndef R3SC_BANK_H
#define R3SC_BANK_H
#include <stddef.h>
#include <stdint.h>
#include "r3sc_manager.h"
/* Memory-backed ROM-bank index; no filesystem/DMA dependency. */
int r3sc_bank_activate(R3SCManager *manager,const uint8_t *index,size_t index_size,const uint8_t *bank,size_t bank_size,const char *room_id);
#endif
