#include "Timer.h"
#include "lcd.h"
#include "open_interface.h"
#include "movement.h"
#include <string.h>
#include <stdio.h>
#include "PuTTyCom.h"
#include "cyBot_Scan.h"
#include "uart.h"

void adc_init(){
    SYSCTL_RCGCADC_R |= 0x1;
    SYSCTL_RCGCGPIO_R |= 0x02;
    GPIO_PORTB_DIR_R &= ~0x10;
    GPIO_PORTB_AFSEL_R |= 0x10;
    GPIO_PORTB_DEN_R &= ~0x10;
    GPIO_PORTB_AMSEL_R |= 0x10;

    ADC0_ACTSS_R &= ~ ADC_ACTSS_ASEN1;
    ADC0_EMUX_R = ADC_EMUX_EM1_PROCESSOR;
    ADC0_SSMUX1_R = 0x0A;
    ADC0_SSCTL1_R = 0x06;
    ADC0_ACTSS_R |= ADC_ACTSS_ASEN1;
}

uint16_t adc_read(){
    uint16_t rawVal;
    ADC0_PSSI_R = ADC_PSSI_SS1;
    while((ADC0_RIS_R & 2) == 0);
    rawVal = ADC0_SSFIFO1_R;
    ADC0_ISC_R = ADC_ISC_IN1;
    return rawVal;
}
