#include <iostream>
#include <unistd.h>     // For close, sleep, usleep, write, read
#include <fcntl.h>      // For O_RDWR, open
#include <sys/ioctl.h>  // For ioctl
#include <linux/i2c-dev.h> // For I2C_SLAVE
#include <string.h>     // For strerror
#include <errno.h>      // For errno
#include <vector>       // For std::vector
#include <algorithm>    // For std::sort
#include <cstdint>      // for uint8_t
#include <string>       // for std::string
#include <stdexcept>    // for std::runtime_error
#include <cmath>        // for floor

// --- TOF250 Constants ---
const int TOF_ADDRESS = 0x52;
const char* I2C_BUS_PATH = "/dev/i2c-1";
const int DIST_REG_START = 0x00;
const int REQUIRED_DELAY_US = 100; // Delay for TOF read

// --- PCA9685 Constants ---
const int PCA9685_ADDRESS = 0x40;
const int I2C_BUS_NUM = 1; // Bus number for pca9685_init

#define PCA9685_MODE1 0x00
#define PCA9685_PRESCALE 0xFE
#define LED0_ON_L 0x06
#define LED0_ON_H 0x07
#define LED0_OFF_L 0x08
#define LED0_OFF_H 0x09
#define ALL_LED_ON_L 0xFA
#define ALL_LED_ON_H 0xFB
#define ALL_LED_OFF_L 0xFC
#define ALL_LED_OFF_H 0xFD

// --- Logic Constants ---
const int MOTOR_CHANNEL_0 = 0;
const int MOTOR_CHANNEL_1 = 1;
const int MOTOR_CHANNEL_2 = 2;
const int MOTOR_CHANNEL_3 = 3;
const int MOTOR_CHANNEL_4 = 4;
const int MOTOR_CHANNEL_5 = 5; // ADDED for new sequence
const int MOTOR_CHANNEL_12 = 12; // NEW
const int MOTOR_CHANNEL_13 = 13; // NEW
 
// Sequence 1 & 2
const int MOTOR_RUN_PWM = 310;     // For Channel 0 (Seq 2)
const int MOTOR_1_RUN_PWM = 440;   // For Channel 1 (Seq 1)
const int MOTOR_3_RUN_PWM = 325;   // For Channel 3 (Seq 2)

// Sequence 3 & 4
const int MOTOR_1_RUN_PWM_SEQ3 = 340; // For Channel 1 (Seq 3)
const int MOTOR_2_RUN_PWM_SEQ4 = 325; // For Channel 2 (Seq 4)
const int MOTOR_4_RUN_PWM_SEQ4 = 352; // For Channel 4 (Seq 4)

// Sequence 5 & 6 (NEW)
const int MOTOR_5_STOP_PWM = 230;     // For Channel 5 (Stop)
const int MOTOR_5_RUN_PWM = 340;      // For Channel 5 (Run)
const int MOTOR_2_RUN_PWM_SEQ6 = 355; // For Channel 2 (Seq 6)
const int MOTOR_4_RUN_PWM_SEQ6 = 322; // For Channel 4 (Seq 6)

// Sequence 7 (NEW)
const int MOTOR_13_POS_1_PWM = 330;
const int MOTOR_12_RUN_PWM = 345;
const int MOTOR_12_STOP_PWM = 335;
const int MOTOR_13_POS_2_PWM = 480; // 요청한 코드 스니펫의 값 (주석 380 아님)

// Stop PWMs
const int MOTOR_STOP_PWM = 330;     // Universal Stop PWM (For Ch 0, Ch 1)
const int MOTOR_2_STOP_PWM = 340;   // Specific Stop PWM for Ch 2
const int MOTOR_3_STOP_PWM = 340;   // Specific Stop PWM for Ch 3
const int MOTOR_4_STOP_PWM = 337;   // Specific Stop PWM for Ch 4
// MOTOR_5_STOP_PWM is defined above
// NEW
const int MOTOR_12_INIT_STOP_PWM = 335; // 채널 12의 초기/최종 정지값
const int MOTOR_13_INIT_STOP_PWM = 330; // 채널 13의 초기/최종 정지값

// Durations
const int DISTANCE_THRESHOLD_MM = 22;
const int MOTOR_1_RUN_DURATION_SEC = 2; // Duration for Seq 1 (and Seq 3)
const int MOTOR_RUN_DURATION_SEC = 13;  // Duration for Seq 2 (Ch 0, Ch 3)
const int MOTOR_SEQ4_DURATION_SEC = 5;  // Duration for Seq 4 (Ch 2, Ch 4)
const int MOTOR_SEQ5_DURATION_SEC = 5;  // Duration for Seq 5 (Ch 5)
const int MOTOR_SEQ6_DURATION_SEC = 6;  // Duration for Seq 6 (Ch 2, 4)
const int LOOP_DELAY_US = 100000; // 100ms loop period


// --- PCA9685 Helper Functions ---

void write_reg(int fd, uint8_t reg, uint8_t value) {
    uint8_t buffer[2] = {reg, value};
    if (write(fd, buffer, 2) != 2) {
        std::cerr << "Failed to write to register " << (int)reg << std::endl;
    }
}

uint8_t read_reg(int fd, uint8_t reg) {
    uint8_t write_buf[1] = {reg};
    if (write(fd, write_buf, 1) != 1) {
        std::cerr << "Failed to write register address for reading: " << (int)reg << std::endl;
    }

    uint8_t read_buf[1];
    if (read(fd, read_buf, 1) != 1) {
         std::cerr << "Failed to read from register " << (int)reg << std::endl;
    }
    return read_buf[0];
}

void pca9685_reset(int fd) {
    write_reg(fd, PCA9685_MODE1, 0x80); // reset
    usleep(10000); // 10ms waiting
}

void pca9685_setAllPWM(int fd, int on, int off) {
    write_reg(fd, ALL_LED_ON_L, on & 0xFF);
    write_reg(fd, ALL_LED_ON_H, on >> 8);
    write_reg(fd, ALL_LED_OFF_L, off & 0xFF);
    write_reg(fd, ALL_LED_OFF_H, off >> 8);
}

void pca9685_setPWMFreq(int fd, float freq) {
    float prescaleval = 25000000.0; // 25MHz inner oscilator
    prescaleval /= 4096.0;       // 12-bit
    prescaleval /= freq;
    prescaleval -= 1.0;

    uint8_t prescale = static_cast<uint8_t>(std::floor(prescaleval + 0.5));

    uint8_t oldmode = read_reg(fd, PCA9685_MODE1);
    uint8_t newmode = (oldmode & 0x7F) | 0x10; // Sleep mode

    write_reg(fd, PCA9685_MODE1, newmode);     // Sleep
    write_reg(fd, PCA9685_PRESCALE, prescale); // Prescale setting
    write_reg(fd, PCA9685_MODE1, oldmode);     // return to original mode

    usleep(5000); // 5ms delay

    write_reg(fd, PCA9685_MODE1, oldmode | 0xA0); // Auto-Increment activation
}

void pca9685_setPWM(int fd, int channel, int on, int off) {
    on = on & 0x0FFF;
    off = off & 0x0FFF;

    write_reg(fd, LED0_ON_L + 4 * channel, on & 0xFF);
    write_reg(fd, LED0_ON_H + 4 * channel, on >> 8);
    write_reg(fd, LED0_OFF_L + 4 * channel, off & 0xFF);
    write_reg(fd, LED0_OFF_H + 4 * channel, off >> 8);
}

int pca9685_init(int bus, int address) {
    std::string i2c_bus_name = "/dev/i2c-" + std::to_string(bus);
    int fd;

    if ((fd = open(i2c_bus_name.c_str(), O_RDWR)) < 0) {
        throw std::runtime_error("Failed to open the i2c bus: " + i2c_bus_name);
    }

    if (ioctl(fd, I2C_SLAVE, address) < 0) {
        close(fd);
        throw std::runtime_error("Failed to acquire bus access and/or talk to slave.");
    }

    return fd;
}

// --- Main Application ---

int main() {
    int tof_fd = -1;
    int pca_fd = -1;

    try {
        // --- 1. Initialize TOF Sensor ---
        if ((tof_fd = open(I2C_BUS_PATH, O_RDWR)) < 0) {
            std::cerr << "Failed to open the I2C bus (" << I2C_BUS_PATH << "): "
                      << strerror(errno) << std::endl;
            return 1;
        }

        if (ioctl(tof_fd, I2C_SLAVE, TOF_ADDRESS) < 0) {
            std::cerr << "Failed to set TOF slave address (0x" << std::hex << TOF_ADDRESS << "): "
                      << strerror(errno) << std::endl;
            close(tof_fd);
            return 1;
        }
        std::cout << "Successfully connected to TOF Sensor at 0x" << std::hex << TOF_ADDRESS << std::endl;

        // --- 2. Initialize PCA9685 ---
        pca_fd = pca9685_init(I2C_BUS_NUM, PCA9685_ADDRESS);
        pca9685_reset(pca_fd);
        pca9685_setPWMFreq(pca_fd, 50.0); // Set 50Hz for motor
        std::cout << "Successfully connected to PCA9685 at 0x" << std::hex << PCA9685_ADDRESS << std::endl;

        // --- 3. Set initial motor state ---
        std::cout << "Setting all motors (Ch " << MOTOR_CHANNEL_0 << ", "
                  << MOTOR_CHANNEL_1 << ", " << MOTOR_CHANNEL_2 << ", " 
                  << MOTOR_CHANNEL_3 << ", " << MOTOR_CHANNEL_4 << ", "
                  << MOTOR_CHANNEL_5 << ", "
                  << MOTOR_CHANNEL_12 << ", " // NEW
                  << MOTOR_CHANNEL_13         // NEW
                  << ") to STOP"
                  << std::endl;
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_0, 0, MOTOR_STOP_PWM);   // Stop Ch 0
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_1, 0, MOTOR_STOP_PWM);   // Stop Ch 1
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_2, 0, MOTOR_2_STOP_PWM);   // Stop Ch 2
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_3, 0, MOTOR_3_STOP_PWM);   // Stop Ch 3
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_4, 0, MOTOR_4_STOP_PWM);   // Stop Ch 4
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_5, 0, MOTOR_5_STOP_PWM);   // Stop Ch 5
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_12, 0, MOTOR_12_INIT_STOP_PWM); // NEW
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_13, 0, MOTOR_13_INIT_STOP_PWM); // NEW
 
        // --- TOF Variables ---
        unsigned char reg_addr = DIST_REG_START;
        unsigned char data_buffer[2];
        const int MEDIAN_BUFFER_SIZE = 5; // Must be odd
        std::vector<int> readings;
        int readIndex = 0;
        int medianDistance = 0;

        // --- Logic State Variables ---
        bool objectWasPresent = false; // State to detect a new object appearance

        // --- 4. Main Loop ---
        while (true) {
            // --- 4a. Read TOF Sensor ---
            if (write(tof_fd, &reg_addr, 1) != 1) {
                std::cerr << "Failed to write TOF register address: " << strerror(errno) << std::endl;
                usleep(LOOP_DELAY_US);
                continue;
            }

            usleep(REQUIRED_DELAY_US); // Short delay required by sensor

            if (read(tof_fd, data_buffer, 2) != 2) {
                std::cerr << "Failed to read 2 bytes from TOF: " << strerror(errno) << std::endl;
                usleep(LOOP_DELAY_US);
                continue;
            }

            int rawDistance = (data_buffer[0] << 8) | data_buffer[1];

            // --- 4b. Apply Median Filter ---
            if (readings.size() < MEDIAN_BUFFER_SIZE) {
                readings.push_back(rawDistance);
                medianDistance = rawDistance;
            } else {
                readings[readIndex] = rawDistance;
                readIndex = (readIndex + 1) % MEDIAN_BUFFER_SIZE;
                std::vector<int> sortedReadings = readings;
                std::sort(sortedReadings.begin(), sortedReadings.end());
                medianDistance = sortedReadings[MEDIAN_BUFFER_SIZE / 2];
            }

            // Print distance on one line
            std::cout << "Distance: " << medianDistance << " mm (Raw: " << rawDistance << " mm)       \r" << std::flush;

            // --- 4c. Motor Control Logic ---
            bool objectIsPresent = (medianDistance <= DISTANCE_THRESHOLD_MM);

            if (objectIsPresent) {
                // Object is currently detected
                if (!objectWasPresent) {
                    // This is a NEW detection event
                    std::cout << std::endl << "Object DETECTED. Starting Full Sequence." << std::endl;
                    
                    // --- Sequence 1: Run Channel 1 ---
                    std::cout << "  Seq 1: Running Channel " << MOTOR_CHANNEL_1 << " (PWM " << MOTOR_1_RUN_PWM << ") for "
                              << MOTOR_1_RUN_DURATION_SEC << "s." << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_1, 0, MOTOR_1_RUN_PWM);
                    sleep(MOTOR_1_RUN_DURATION_SEC);
                    
                    std::cout << "  Seq 1: Stopping Channel " << MOTOR_CHANNEL_1 << "." << std::endl;
                    
                    usleep(500000); // 0.5s pause between sequences

                    // --- Sequence 2: Run Channel 0 and 3 ---
                    std::cout << "  Seq 2: Running Channel " << MOTOR_CHANNEL_0 << " (PWM " << MOTOR_RUN_PWM << ") and Channel "
                              << MOTOR_CHANNEL_3 << " (PWM " << MOTOR_3_RUN_PWM << ") for "
                              << MOTOR_RUN_DURATION_SEC << "s." << std::endl;
                    
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_0, 0, MOTOR_RUN_PWM);
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_3, 0, MOTOR_3_RUN_PWM);

                    sleep(MOTOR_RUN_DURATION_SEC); 
                    
                    std::cout << std::endl << "  Seq 2: " << MOTOR_RUN_DURATION_SEC << " seconds finished. Stopping motors." << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_0, 0, MOTOR_STOP_PWM);
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_3, 0, MOTOR_3_STOP_PWM);
                   
                    usleep(500000); // 0.5s pause between sequences

                    // --- Sequence 3: Run Channel 1 ---
                    std::cout << "  Seq 3: Running Channel " << MOTOR_CHANNEL_1 << " (PWM " << MOTOR_1_RUN_PWM_SEQ3 << ") for "
                              << MOTOR_1_RUN_DURATION_SEC << "s." << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_1, 0, MOTOR_1_RUN_PWM_SEQ3);
                    sleep(MOTOR_1_RUN_DURATION_SEC); // Re-using 2s duration
                    
                    std::cout << "  Seq 3: Stopping Channel " << MOTOR_CHANNEL_1 << "." << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_1, 0, MOTOR_STOP_PWM); // Use universal stop
                    
                    usleep(12000000); // 0.5s pause between sequences

                    // --- Sequence 4: Run Channel 2 and 4 ---
                    std::cout << "  Seq 4: Running Channel " << MOTOR_CHANNEL_2 << " (PWM " << MOTOR_2_RUN_PWM_SEQ4 << ") and Channel "
                              << MOTOR_CHANNEL_4 << " (PWM " << MOTOR_4_RUN_PWM_SEQ4 << ") for "
                              << MOTOR_SEQ4_DURATION_SEC << "s." << std::endl;
                    
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_2, 0, MOTOR_2_RUN_PWM_SEQ4);
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_4, 0, MOTOR_4_RUN_PWM_SEQ4);

                    sleep(MOTOR_SEQ4_DURATION_SEC);
                    
                    std::cout << std::endl << "  Seq 4: " << MOTOR_SEQ4_DURATION_SEC << " seconds finished. Stopping motors." << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_2, 0, MOTOR_2_STOP_PWM);
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_4, 0, MOTOR_4_STOP_PWM);
                   
                    usleep(500000); // 0.5s pause between sequences

                    // --- Sequence 5: Run Channel 5 (New) ---
                    std::cout << "  Seq 5: Running Channel " << MOTOR_CHANNEL_5 << " (PWM " << MOTOR_5_RUN_PWM << ") for "
                              << MOTOR_SEQ5_DURATION_SEC << "s." << std::endl;
                    
                    // Specific request: 230 -> 340
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_5, 0, MOTOR_5_STOP_PWM); 
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_5, 0, MOTOR_5_RUN_PWM);
                    
                    sleep(MOTOR_SEQ5_DURATION_SEC);
                    
                    std::cout << "  Seq 5: Stopping Channel " << MOTOR_CHANNEL_5 << "." << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_5, 0, MOTOR_5_STOP_PWM); // Back to 230

                    usleep(500000); // 0.5s pause between sequences

                    // --- Sequence 6: Run Channel 2 and 4 (New) ---
                    std::cout << "  Seq 6: Running Channel " << MOTOR_CHANNEL_2 << " (PWM " << MOTOR_2_RUN_PWM_SEQ6 << ") and Channel "
                              << MOTOR_CHANNEL_4 << " (PWM " << MOTOR_4_RUN_PWM_SEQ6 << ") for "
                              << MOTOR_SEQ6_DURATION_SEC << "s." << std::endl;

                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_2, 0, MOTOR_2_RUN_PWM_SEQ6);
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_4, 0, MOTOR_4_RUN_PWM_SEQ6);

                    sleep(MOTOR_SEQ6_DURATION_SEC);

                    // --- Sequence 6 Stop --- (기존 Seq 7을 이름 변경)
                    std::cout << std::endl << "  Seq 6 Stop: Final stop for Channel " << MOTOR_CHANNEL_2 << " and " << MOTOR_CHANNEL_4 << "." << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_2, 0, MOTOR_2_STOP_PWM);
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_4, 0, MOTOR_4_STOP_PWM);

                    usleep(12000000); // 0.5s pause

                    // --- Sequence 7: Control Channels 12 & 13 (NEW) ---
                    std::cout << std::endl << "--- Starting Sequence 7 (Ch 12 & 13) ---" << std::endl;

                    // 1. Setting motor 13 (channel 13) to 330
                    std::cout << "  Seq 7.1: Setting motor 13 (channel " << MOTOR_CHANNEL_13 << ") to " << MOTOR_13_POS_1_PWM << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_13, 0, MOTOR_13_POS_1_PWM);
                    sleep(1); // Wait 1 second

                    // 2. Run motor 12 (channel 12) at 345 for 1200ms, then stop it by setting to 335
                    std::cout << "  Seq 7.2: Running motor 12 (channel " << MOTOR_CHANNEL_12 << ") at " << MOTOR_12_RUN_PWM << " for 1200ms" << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_12, 0, MOTOR_12_RUN_PWM);
                    usleep(1000000); // Wait 1200ms (1.2 seconds)

                    std::cout << "     Stopping motor 12 (setting to " << MOTOR_12_STOP_PWM << ")" << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_12, 0, MOTOR_12_STOP_PWM);
                    sleep(1); // Wait 1 second after stopping

                    // 3. Set motor 13 (channel 13) to 400
                    std::cout << "  Seq 7.3: Setting motor 13 (channel " << MOTOR_CHANNEL_13 << ") to " << MOTOR_13_POS_2_PWM << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_13, 0, MOTOR_13_POS_2_PWM);
                    sleep(2); // Wait 2 seconds

                    // --- Sequence 8: 5s Wait and Final Stop for Ch 13 (NEW) ---
                    std::cout << "  Seq 8: Waiting 5 seconds..." << std::endl;
                    sleep(5); // 5초 대기

                    std::cout << "  Seq 8: Final stop for motor 13 (channel " << MOTOR_CHANNEL_13 << "), setting to " << MOTOR_13_INIT_STOP_PWM << std::endl;
                    pca9685_setPWM(pca_fd, MOTOR_CHANNEL_13, 0, MOTOR_13_INIT_STOP_PWM); // 13번 채널 330으로 설정
                    
                    usleep(500000); // 서보가 마지막 위치로 이동할 시간 확보

                    // --- End of Sequence ---
                    std::cout << "Full sequence complete. Exiting program." << std::endl;
                    break; // Exit the while(true) loop
                }
                
                objectWasPresent = true; // Mark that object is here
            } else {
                // Object is NOT detected
                if (objectWasPresent) {
                    // Object was just removed
                    std::cout << std::endl << "Object removed. Ready for new detection." << std::endl;
                }
                objectWasPresent = false; // Mark that object is gone
            }


            // --- 4d. Loop Delay ---
            // This delay is now only active *before* detection
            usleep(LOOP_DELAY_US); 
        }

    } catch (const std::exception& e) {
        std::cerr << "Runtime Error: " << e.what() << std::endl;
        if (pca_fd != -1) {
            // Failsafe: stop all motors
            std::cerr << "Failsafe: Stopping all PWM channels." << std::endl;
            pca9685_setAllPWM(pca_fd, 0, 0);
        }
        // Close FDs
        if (tof_fd != -1) close(tof_fd);
        if (pca_fd != -1) close(pca_fd);
        return 1;
    }

    // --- Cleanup (now reachable) ---
    if (pca_fd != -1) {
        std::cout << "Shutting down motors." << std::endl;
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_0, 0, MOTOR_STOP_PWM);
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_1, 0, MOTOR_STOP_PWM);
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_2, 0, MOTOR_2_STOP_PWM);
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_3, 0, MOTOR_3_STOP_PWM);
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_4, 0, MOTOR_4_STOP_PWM);
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_5, 0, MOTOR_5_STOP_PWM); // ADDED
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_12, 0, MOTOR_12_INIT_STOP_PWM); // NEW
        pca9685_setPWM(pca_fd, MOTOR_CHANNEL_13, 0, MOTOR_13_INIT_STOP_PWM); // NEW
        pca9685_setAllPWM(pca_fd, 0, 0);
        close(pca_fd);
    }
    if (tof_fd != -1) {
        close(tof_fd);
    }

    std::cout << "Program finished." << std::endl;
    return 0;
}