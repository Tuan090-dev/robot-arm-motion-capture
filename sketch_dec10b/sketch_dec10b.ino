#include <Wire.h> 
#include <Servo.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca9685 = Adafruit_PWMServoDriver();
#define SERVOMIN 102
#define SERVOMAX 512

Servo myservo1;
Servo myservo2;
Servo myservo3;
Servo myservo4;

int goc1 = 0;
int goc2 = 0;
int goc3 = 0;
int goc4 = 0;
int goc5 = 0;
int goc6 = 0;
int goc7 = 0;

int mapAngleToPWM(int angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

void rot()
{
  
}

void setup()
{  
  Serial.begin(115200);           
  myservo1.attach(9);
  myservo1.write(160);
  delay(500);
  
  myservo2.attach(10);
  myservo2.write(20);
  delay(500);
  
  pca9685.begin();
  pca9685.setPWMFreq(50);
  pca9685.setPWM(0, 0, mapAngleToPWM(90)); // Kênh 0
  pca9685.setPWM(1, 0, mapAngleToPWM(110)); // Kênh 0
  pca9685.setPWM(2, 0, mapAngleToPWM(90)); // Kênh 0
  pca9685.setPWM(3, 0, mapAngleToPWM(90));
  pca9685.setPWM(4, 0, mapAngleToPWM(135));
  delay(500); 
}

void loop()
{
  while(Serial.available() == 0)
  {
  }

  String data = "";
  data = Serial.readStringUntil('\n');

  goc1 = 90 - data.substring(0, 2).toInt();
  goc2 = data.substring(2, 4).toInt();
  goc3 = 90+data.substring(4, 7).toInt();
  goc4 = 30 - (-1*data.substring(7, 10).toInt());
  goc5 = 90 - data.substring(10, 13).toInt();
  goc6 = 90 + data.substring(13, 16).toInt();
  goc7 = 120 + data.substring(16, 19).toInt();
  myservo1.write(goc1 * 2);
  myservo2.write(goc2 * 2);
  pca9685.setPWM(0, 0, mapAngleToPWM(goc3)); // Kênh 0
  pca9685.setPWM(1, 0, mapAngleToPWM(goc4)); // Kênh 0
  pca9685.setPWM(2, 0, mapAngleToPWM(goc5)); // Kênh 0
  pca9685.setPWM(3, 0, mapAngleToPWM(goc6)); // Kênh 0
  pca9685.setPWM(4, 0, mapAngleToPWM(goc7)); // Kênh 0
}
