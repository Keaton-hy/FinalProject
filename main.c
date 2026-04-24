#include "uart.h"
#include <lcd.h>
#include <ping_template.h>
#include <Timer.h>
#include <servo.h>
#include <button.h>
#include <PuTTyCom.h>
#include <open_interface.h>
#include <stdio.h>


// Uncomment or add any include directives that are needed

#warning "Possible unimplemented functions"
#define REPLACEME 0

static int is_drive_command(char command) {
    return command == 'w' || command == 's' || command == 'a' || command == 'd' ||
           command == 'g' || command == 'h' || command == 'j' || command == 'k';
}

static void send_oi_status(oi_t *sensor_data) {
    char buffer[120];

    oi_update(sensor_data);
    sprintf(buffer,
            "OI: bumpL=%d bumpR=%d cliffL=%d cliffFL=%d cliffFR=%d cliffR=%d dist=%.2f angle=%.2f\r\n",
            sensor_data->bumpLeft,
            sensor_data->bumpRight,
            sensor_data->cliffLeft,
            sensor_data->cliffFrontLeft,
            sensor_data->cliffFrontRight,
            sensor_data->cliffRight,
            sensor_data->distance,
            sensor_data->angle);
    uart_sendStr(buffer);
}

int main(void) {
    int speed = 100;
    char last_drive_command = 0;
    char buffer[32];
    oi_t *sensor_data;

	timer_init(); // Must be called before lcd_init(), which uses timer functions
	lcd_init();
	uart_init();
	servo_init();
	ping_init();
	button_init();
	sensor_data = oi_alloc();
	oi_init(sensor_data);

	uart_sendStr("READY\r\n");
	lcd_printf("READY");

	while(1) {
	    char command = uart_receive();

	    if (is_drive_command(command)) {
	        oi_update(sensor_data);

	        if (sensor_data->bumpLeft || sensor_data->bumpRight) {
	            oi_setWheels(0, 0);
	            uart_sendStr("EMERGENCY: bump\r\n");
	            if (command != 's') {
	                continue;
	            }
	        }

	        if (sensor_data->cliffLeft || sensor_data->cliffFrontLeft ||
	            sensor_data->cliffFrontRight || sensor_data->cliffRight) {
	            oi_setWheels(0, 0);
	            uart_sendStr("EMERGENCY: cliff\r\n");
	            if (command != 's') {
	                continue;
	            }
	        }
	    }

	    if (command == 'v') {
	        int parsed_speed = 0;
	        char digit = uart_receive();
	        while (digit >= '0' && digit <= '9') {
	            parsed_speed = parsed_speed * 10 + (digit - '0');
	            if (parsed_speed > 500) {
	                parsed_speed = 500;
	            }
	            digit = uart_receive();
	        }
	        if (parsed_speed < 0) {
	            parsed_speed = 0;
	        }
	        speed = parsed_speed;
	        sprintf(buffer, "CMD: speed %d\r\n", speed);
	        uart_sendStr(buffer);
	    } else if (command == 'p') {
	        send_Pingscan(ping_getDistance());
	    } else if (command == 'o') {
	        send_oi_status(sensor_data);
	    } else if (command == 't') {
	        uart_sendStr("TEST: wheels forward 500ms\r\n");
	        oi_setWheels(100, 100);
	        timer_waitMillis(500);
	        oi_setWheels(0, 0);
	        send_oi_status(sensor_data);
	    } else if (command == 'm') {
	        uart_sendStr("SWEEP: not implemented\r\n");
	    } else if (command == 'w') {
	        oi_setWheels(speed, speed);
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: forward\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 's') {
	        oi_setWheels(-speed, -speed);
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: backward\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 'a') {
	        oi_setWheels(speed / 2, -(speed / 2));
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: left\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 'd') {
	        oi_setWheels(-(speed / 2), speed / 2);
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: right\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 'g') {
	        oi_setWheels(speed, speed / 2);
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: forward-left\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 'h') {
	        oi_setWheels(speed / 2, speed);
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: forward-right\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 'j') {
	        oi_setWheels(-speed, -(speed / 2));
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: backward-left\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 'k') {
	        oi_setWheels(-(speed / 2), -speed);
	        if (last_drive_command != command) {
	            uart_sendStr("CMD: backward-right\r\n");
	        }
	        last_drive_command = command;
	    } else if (command == 'x') {
	        oi_setWheels(0, 0);
	        last_drive_command = 0;
	        uart_sendStr("CMD: stop\r\n");
	    } else if (command == 'q') {
	        oi_setWheels(0, 0);
	        last_drive_command = 0;
	        uart_sendStr("CMD: standby\r\n");
	    } else {
	        uart_sendStr("UNKNOWN: ");
	        uart_sendChar(command);
	        uart_sendStr("\r\n");
	    }
	}

	return 0;

}
