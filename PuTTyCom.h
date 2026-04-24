/*
 * PuTTyCom.h
 *
 *  Created on: Feb 13, 2026
 *      Author: tholtz24
 */

#ifndef PUTTYCOM_H_
#define PUTTYCOM_H_

void send_string(int direction);

void send_num(int angle, float distance);

void sendButtonMessage(int button);

void send_IRscan(int angle, int IR, float ping);

void send_Pingscan(float ping);

//void test(char buffer);

#endif /* PUTTYCOM_H_ */
