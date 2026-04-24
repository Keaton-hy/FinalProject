/*
 * movement.c
 *
 *  Created on: Feb 6, 2026
 *      Author: tholtz24
 */

#include "open_interface.h"
#include "PuTTyCom.h"

void turn_left(oi_t *sensor, double degrees){ //Function declaration and I'm running on the assumption that an already declared sensor is being passed.

    double turnSum = 0; //Declaration of the variable that will keep track of the total turned degrees.

    oi_setWheels(100, -100); //Set the right wheel to spin forward and the left to go back causing the Roomba to turn left.

    while (turnSum < degrees){ //Set up the while loop check for the actual turn in degrees and to stop when we hit it.

        oi_update(sensor); //This update the sensor to the correct data allowing it to be accurately added to the current turn degrees in the next step.

        turnSum += sensor -> angle; //This adds on the new angle that the Roomba has turned since it was last updated.

    }

    oi_setWheels(0, 0); //This stops the wheels so whatever the next function is may execute without the Roomba having already shifted/have its wheels going.

}

void turn_right(oi_t *sensor, double degrees){ //Function declaration and I'm running on the assumption that an already declared sensor is being passed.

    double turnSum = 0; //Declaration of the variable that will keep track of the total turned degrees.

    oi_setWheels(-100, 100); //Set the right wheel to spin back and the left to go forward causing the Roomba to turn right.

    while (turnSum > degrees){ //Set up the while loop check for the actual turn in degrees and to stop when we hit it. This is greater than because it is turning right it will be trying to go until it hits -270 to make the box shape.

            oi_update(sensor); //This update the sensor to the correct data allowing it to be accurately added to the current turn degrees in the next step.

                turnSum += sensor -> angle; //This adds on the new angle that the Roomba has turned since it was last updated.

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
    double sum = 0;
    oi_setWheels(100,100); //move forward at full speed
    while (sum < distance_mm) {
        oi_update(sensor_data);

        if (sensor_data -> bumpLeft){
            oi_setWheels(0,0);
            move_backward(sensor_data, -150);
            send_string(1);
            break;
        } else if (sensor_data -> bumpRight){
            oi_setWheels(0,0);
            move_backward(sensor_data, -150);
            send_string(2);
            break;
        } else if (sensor_data -> bumpLeft && sensor_data -> bumpRight){
            oi_setWheels(0,0);
            move_backward(sensor_data, -150);
            send_string(3);
            break;
        } else if (sensor_data -> cliffLeft){
            oi_setWheels(0,0);
            move_backward(sensor_data, -150);
            send_string(4);
            break;
        } else if (sensor_data -> cliffFrontLeft){
            oi_setWheels(0,0);
            move_backward(sensor_data, -150);
            send_string(5);
            break;
        } else if (sensor_data -> cliffFrontRight){
            oi_setWheels(0,0);
            move_backward(sensor_data, -150);
            send_string(6);
            break;
        } else if (sensor_data -> cliffRight){
            oi_setWheels(0,0);
            move_backward(sensor_data, -150);
            send_string(7);
            break;
        }

        sum += sensor_data -> distance; // use -> notation since pointer
    }
    oi_setWheels(0,0); //stop

    return sum;
}
