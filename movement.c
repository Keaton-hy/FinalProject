/*
 * movement.c
 *
 *  Created on: Feb 6, 2026
 *      Author: tholtz24
 */

#include "open_interface.h"

void turn_left(oi_t *sensor, double degrees){ //Function declaration and I'm running on the assumption that an already declared sensor is being passed.

    if (degrees > 5.75){

        degrees -= 5.75;

    }

    double turnSum = 0; //Declaration of the variable that will keep track of the total turned degrees.

    oi_setWheels(50, -50); //Set the right wheel to spin forward and the left to go back causing the Roomba to turn left.

    while (turnSum < degrees){ //Set up the while loop check for the actual turn in degrees and to stop when we hit it.

        oi_update(sensor); //This update the sensor to the correct data allowing it to be accurately added to the current turn degrees in the next step.

        turnSum += sensor -> angle; //This adds on the new angle that the Roomba has turned since it was last updated.

        oi_setWheels(50, -50); //Set the right wheel to spin forward and the left to go back causing the Roomba to turn left.

    }

    oi_setWheels(0, 0); //This stops the wheels so whatever the next function is may execute without the Roomba having already shifted/have its wheels going.

}

void turn_right(oi_t *sensor, double degrees){ //Function declaration and I'm running on the assumption that an already declared sensor is being passed.

    if (degrees < -5.75){

        degrees += 5.75;

    }

    double turnSum = 0; //Declaration of the variable that will keep track of the total turned degrees.

    oi_setWheels(-50, 50); //Set the right wheel to spin back and the left to go forward causing the Roomba to turn right.

    while (turnSum > degrees){ //Set up the while loop check for the actual turn in degrees and to stop when we hit it. This is greater than because it is turning right it will be trying to go until it hits -270 to make the box shape.

            oi_update(sensor); //This update the sensor to the correct data allowing it to be accurately added to the current turn degrees in the next step.

            turnSum += sensor -> angle; //This adds on the new angle that the Roomba has turned since it was last updated.

            oi_setWheels(-50, 50); //Set the right wheel to spin back and the left to go forward causing the Roomba to turn right.

    }

    oi_setWheels(0, 0); //This stops the wheels so whatever the next function is may execute without the Roomba having already shifted/have its wheels going.

}

void move_backward(oi_t *sensor_data, double distance_mm){
    double sum = 0; // distance member in oi_t struct is type double
    oi_setWheels(-100,-100); //move forward at full speed
    while (sum > distance_mm) {
        oi_update(sensor_data);

            sum += sensor_data -> distance; // use -> notation since pointer
        }
        oi_setWheels(0,0); //stop
    }

double move_forward(oi_t *sensor_data, double distance_mm){
    double sum = 0; // distance member in oi_t struct is type double
    double reScan = 0;
    oi_setWheels(100,100); //move forward at full speed
    while (sum < distance_mm) {
        oi_update(sensor_data);

        if (sensor_data -> bumpLeft){
            oi_setWheels(0,0);
                    move_backward(sensor_data, -150);
                    turn_right(sensor_data, -84.25);
                    move_forward(sensor_data, 250);
                    turn_left(sensor_data, 84.25);
                    sum -= 150;
                    reScan = 1;
                    oi_setWheels(100,100);
                    oi_update(sensor_data);
        } else if (sensor_data -> bumpRight){
            oi_setWheels(0,0);
             move_backward(sensor_data, -150);
              turn_left(sensor_data, 84.25);
                 move_forward(sensor_data, 250);
            turn_right(sensor_data, -84.25);
            sum -= 150;
            reScan = 1;
                                    oi_setWheels(100,100);
                                    oi_update(sensor_data);
        } else if (sensor_data -> bumpLeft && sensor_data -> bumpRight){
            oi_setWheels(0,0);
                    move_backward(sensor_data, -150);
                    turn_right(sensor_data, -84.25);
                    move_forward(sensor_data, 250);
                    turn_left(sensor_data, 84.25);
                    sum -= 150;
                                        oi_setWheels(100,100);
                                        oi_update(sensor_data);
                                        reScan = 1;
        }

        sum += sensor_data -> distance; // use -> notation since pointer

        oi_setWheels(100,100); //move forward at full speed
    }
    oi_setWheels(0,0); //stop

    return reScan;
}
