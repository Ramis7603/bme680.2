# bme680.2
# Pico W – BME680 Sensorprojekt

Dieses Projekt nutzt einen **Raspberry Pi Pico W** und einen **BME680 Sensor**, um Umweltdaten zu messen.

Der Pico W verbindet sich mit **WLAN** und sendet die Messwerte an einen **MQTT-Server**.  
Optional können die Daten auch **per E-Mail** verschickt werden.

---

## Funktion

- Messung von:
  - Temperatur
  - Luftfeuchtigkeit
  - Luftdruck
  - Gaswiderstand
- WLAN-Verbindung mit dem Pico W
- Senden der Daten per **MQTT** im JSON-Format
- Optionaler **E-Mail-Versand**

---

## MQTT

Die Messwerte werden alle **2 Sekunden** an einen MQTT-Broker gesendet.

Beispiel:
```json
{
  "temperature": 22.4,
  "humidity": 48.1,
  "pressure": 1012.3,
  "gas_resistance": 123456
}
```

---

## E-Mail (optional)

-EMAIL_ENABLED = True   # E-Mail aktiv
-EMAIL_ENABLED = False  # E-Mail deaktiviert
