import time
from machine import Pin, I2C
from vl53l0x import VL53L0X
#------------------------------------------------
# Hier kannst du weitere Bibliotheken importieren
def main():
    # Hier treffen wir Vorbereitungen für den Sensor. Hier sollte nichts geändert werden.
    sda = Pin(13)
    scl = Pin(14)
    i2c = I2C(0, sda=sda, scl=scl)
    if i2c.scan():
        tof = VL53L0X(i2c)
    budget = tof.measurement_timing_budget_us
    tof.set_measurement_timing_budget(40000)
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 12)
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 8)
    #------------------------------------------------
    # Hier können weiter Codezeilen eingefügt werden.
    # Diese werden nur einmal ausgeführt.
    #------------------------------------------------
    while True:
        #------------------------------------------------
        # Hier können weiter Codezeilen eingefügt werden.
        #------------------------------------------------
        time.sleep_ms(50)
        
if __name__ == "__main__":
    main()