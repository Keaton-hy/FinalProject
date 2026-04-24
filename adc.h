#include "Timer.h"
#include "lcd.h"
#include "open_interface.h"
#include "movement.h"
#include <string.h>
#include <stdio.h>
#include "PuTTyCom.h"
#include "cyBot_Scan.h"
#include "uart.h"

void adc_init(void);

uint16_t adc_read(void);
