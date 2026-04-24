
#include <string.h>
#include <stdio.h>
#include "uart.h"

void send_string(int objectNum, int angle, float distance, float radialWidth){
    char buffer[50]; //sets up the string to be used for the data

    sprintf(buffer, "Object %d:  %d  %.2f  %.2f", objectNum, angle, distance, radialWidth); //changes the data into a string

    int j;

    for (j = 0; buffer[j] != '\0'; j++){

    uart_sendChar(buffer[j]); //sends the data over to the PuTTy bit by bit
    }

    uart_sendChar('\n');
    uart_sendChar('\r');
}

/*void send_num(int angle, float distance){
    char buffer[50]; //sets up the string to be used for the data

    sprintf(buffer, "%d    %.2f", angle, distance); //changes the data into a string

    int j;

    for (j = 0; buffer[j] != '\0'; j++){

    cyBot_sendByte(buffer[j]); //sends the data over to the PuTTy bit by bit
    }

    cyBot_sendByte('\n');
    cyBot_sendByte('\r');
}

void sendButtonMessage(uint8_t button){
    char buffer[50]; //sets up the string to be used for the data

    if (button == 4){
        sprintf(buffer, "Test Message.");
    } else if (button == 3){
        sprintf(buffer, "This is another message.");
    } else if (button == 2){
        sprintf(buffer, "Sure, another message.");
    } else if (button == 1){
        sprintf(buffer, "This was a message.");
    } else {
        sprintf(buffer, "");
    }

    int j;

    if (strlen(buffer) != 0){
        for (j = 0; buffer[j] != '\0'; j++){
            cyBot_sendByte(buffer[j]); //sends the data over to the PuTTy bit by bit
        }
        cyBot_sendByte('\n');
        cyBot_sendByte('\r');
    }

    void test(char buffer){

        uart_sendChar(buffer); //sends the data over to the PuTTy bit by bit

        if (buffer == '\r'){
        uart_sendChar('\n');
        }
    }*/

   /* void send_IRscan(int angle, int IR, float ping){
        char buffer[50]; //sets up the string to be used for the data

        sprintf(buffer, "Scan at: %d, IR: %d, Ping: %.2f", angle, IR, ping); //changes the data into a string

        int j;

        for (j = 0; buffer[j] != '\0'; j++){

        uart_sendChar(buffer[j]); //sends the data over to the PuTTy bit by bit
        }

        uart_sendChar('\n');
        uart_sendChar('\r');
}*/
    void send_Pingscan(float ping){
           char buffer[25]; //sets up the string to be used for the data

           sprintf(buffer, "Ping: %.2f", ping); //changes the data into a string

           int j;

           for (j = 0; buffer[j] != '\0'; j++){

           uart_sendChar(buffer[j]); //sends the data over to the PuTTy bit by bit
           }

           uart_sendChar('\n');
           uart_sendChar('\r');
   }
