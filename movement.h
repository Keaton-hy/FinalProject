/*
 * movement.h
 *
 *  Created on: Feb 6, 2026
 *      Author: tholtz24
 */

#ifndef MOVEMENT_H_
#define MOVEMENT_H_

double move_forward(oi_t *sensor_data, double distance_mm);

void turn_left(oi_t *sensor, double degrees);

void turn_right(oi_t *sensor, double degrees);

double move_backward(oi_t *sensor_data, double distance_mm);

#endif /* MOVEMENT_H_ */
