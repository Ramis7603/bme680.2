from machine import Pin, I2C
from bme680 import BME680_I2C
import time
import network
from simple import MQTTClient
import json # Für die Formatierung der Daten als JSON
import ubinascii # Für eine eindeutige Client ID
import random # Optional: für eine eindeutige Client ID
from umail import SMTP



# --- KONFIGURATION ANPASSEN! ---

# WLAN-Zugangsdaten (Deine sind bereits im Code)
WIFI_SSID = 'dd-wrt'
WIFI_PASSWORD = '54tzck23'

# MQTT-Einstellungen
MQTT_BROKER = "192.168.1.109"###  # Z.B. "192.168.1.10" oder "broker.hivemq.com"
MQTT_PORT = 1883
# Erstellt eine eindeutige Client-ID basierend auf der Pico-ID
CLIENT_ID = b"pico_bme680_" + ubinascii.hexlify(machine.unique_id()) 
TOPIC = "home/environment/bme680"### # Das Topic, unter dem die Daten gesendet werden


# I2C-Pins für den BME680 (GP4/SDA, GP5/SCL wie in deinem Code)
I2C_SDA_PIN = 4
I2C_SCL_PIN = 5

# Sensor initialisieren
i2c = I2C(0, sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=100000)
sensor = BME680_I2C(i2c)

# --- NEUE KONFIGURATION FÜR E-MAIL ---
EMAIL_ENABLED = False # NEUES BOOLEAN: Auf False setzen, um E-Mail zu deaktivieren

# SMTP-Einstellungen (für den Absender, z.B. Gmail)
SMTP_SERVER = "smtp.gmail.com"  
SMTP_PORT = 465                 # 587 (TLS/STARTTLS) oder 465 (SSL)
SMTP_SENDER_EMAIL = "alisoleimani7603@gmail.com"###
SMTP_APP_PASSWORD = "vdzh pnbz conv bzqs"### # SEHR WICHTIG: App-Passwort verwenden!

# E-Mail-Einstellungen
EMAIL_RECIPIENT = "a.soleimani.tadi@fds-limburg.schule"###
EMAIL_SUBJECT = "BME680 Messdaten-Alarm vom Pico W"
# Sendeintervall für E-Mail (z.B. alle 30 Minuten, 1800 Sekunden)
EMAIL_SEND_INTERVAL_SECONDS = 1800 
last_email_sent_time = 0 # Variable zur Zeitmessung

# --- FUNKTIONEN ---

def connect_to_internet(ssid, password):
    """Verbindet den Pico W mit dem WLAN."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    max_wait = 15
    while max_wait > 0:
      if wlan.status() < 0 or wlan.status() >= 3:
        break
      max_wait -= 1
      print('WLAN: warte auf Verbindung...')
      time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('WLAN-Verbindung fehlgeschlagen!')
    else:
      print('WLAN: verbunden!')
      print('IP-Adresse:', wlan.ifconfig()[0])
      
def send_email(subject, body, to_email):
    """Sendet eine E-Mail über den konfigurierten SMTP-Server."""
    global last_email_sent_time
    
    print("📧 E-Mail: Versuche, Mail zu senden...")
    try:
        # 1. Nachricht zusammenstellen
        msg = "Subject: {}\r\nTo: {}\r\nFrom: {}\r\n\r\n{}".format(
            subject, to_email, SMTP_SENDER_EMAIL, body)
            
        # 2. SMTP-Client initialisieren.
        # WICHTIG: Port 465 verwenden und 'ssl=True' oder 'ssl=ussl' übergeben
        # Die genaue Syntax hängt von der umail-Version ab, oft ist es 'ssl=True' 
        # oder 'ssl=ussl', aber wir versuchen es mit dem gängigen 'ssl=True'
        smtp = SMTP(SMTP_SERVER, SMTP_PORT, 
                    username=SMTP_SENDER_EMAIL, password=SMTP_APP_PASSWORD,
                    ssl=True) # <<< KORREKTUR: Verwenden von ssl=True für Port 465
        
        # 3. Empfänger festlegen
        smtp.to(to_email, mail_from=SMTP_SENDER_EMAIL)
        
        # 4. Die Nachricht senden
        code, resp = smtp.send(msg.encode('utf-8'))
        
        smtp.quit()
        
        last_email_sent_time = time.time()
        print("📧 E-Mail: erfolgreich an {} gesendet. Antwort: {}".format(to_email, resp.decode()))
        return True
    except Exception as e:
        # HINWEIS: Wenn 'ssl=True' fehlschlägt, ist die einzige andere Option 
        # eine sehr alte umail-Version, die SSL gar nicht unterstützt.
        print("📧 E-Mail: Senden fehlgeschlagen! Fehler:", e)
        return False

def connect_mqtt():
    """Stellt die Verbindung zum MQTT-Broker her."""
    print("MQTT: Verbinde mit Broker %s..." % MQTT_BROKER)
    try:
        # Initialisiert den Client mit ID, Broker und Port
        client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT) 
        client.connect()
        print('MQTT: Verbindung erfolgreich.')
        return client
    except Exception as e:
        print('MQTT: Verbindung fehlgeschlagen! Fehler:', e)
        time.sleep(5)
        raise # Wirf den Fehler, damit der Haupt-Loop reagieren kann

# --- HAUPTPROGRAMM ---

# 1. WLAN verbinden
try:
    connect_to_internet(WIFI_SSID, WIFI_PASSWORD)
except RuntimeError as e:
    print(e)
    # Beende das Skript oder versuche es später erneut
    while True:
        time.sleep(60) 

# 2. MQTT-Client initialisieren
mqtt_client = connect_mqtt()

# 3. Haupt-Loop zum Lesen und Senden
while True:
    current_time = time.time()
    try:
        # ... (Sensorwerte lesen wie im Original-Code) ...
        temp = sensor.temperature
        hum = sensor.humidity
        pres = sensor.pressure
        gas = sensor.gas

        # Daten als Python-Dictionary formatieren
        data = {
            "temperature": round(temp, 2),
            "humidity": round(hum, 2),
            "pressure": round(pres, 2),
            "gas_resistance": gas,
        }
        
        # Dictionary in einen JSON-String umwandeln (Payload)
        message = json.dumps(data)
        
        # --- MQTT-LOGIK (Wie im Original) ---
        mqtt_client.publish(TOPIC.encode(), message.encode())
        
        print("-----------------------------")
        # ... (Ausgabe der Sensorwerte wie im Original) ...
        print("📊 Sensorwerte BME680:")
        print("🌡 Temperatur: {:.2f} °C".format(temp))
        print("💧 Feuchtigkeit: {:.2f} %".format(hum))
        print("⚙️ Druck: {:.2f} hPa".format(pres))
        print("💨 Gaswiderstand: {} Ohm".format(gas))
        print("\nMQTT: Gesendet an Topic '{}': {}".format(TOPIC, message))
        
        
        # --- NEUE E-MAIL-LOGIK ---
        if EMAIL_ENABLED:
            # Prüfen, ob das Intervall seit der letzten E-Mail abgelaufen ist
            if (current_time - last_email_sent_time) >= EMAIL_SEND_INTERVAL_SECONDS:
                print("")
                print("--- E-Mail Intervall erreicht. ---")
                
                # E-Mail-Inhalt (kann angepasst werden)
                email_body = (
                    "Aktuelle Messdaten vom BME680:\n"
                    "Temperatur: {:.2f} °C\n".format(temp) +
                    "Feuchtigkeit: {:.2f} %\n".format(hum) +
                    "Druck: {:.2f} hPa\n".format(pres) +
                    "Gaswiderstand: {} Ohm\n".format(gas)
                )
                
                send_email(EMAIL_SUBJECT, email_body, EMAIL_RECIPIENT)
            else:
                remaining = EMAIL_SEND_INTERVAL_SECONDS - (current_time - last_email_sent_time)
                print(f"📧 E-Mail: Nächster Versand in ca. {int(remaining)} Sekunden.")


    except Exception as e:
        print("Fehler im Haupt-Loop (Lesen/Senden/E-Mail):", e)
        # ... (Wiederherstellungslogik wie im Original) ...
        try:
            mqtt_client = connect_mqtt()
        except Exception:
            print("Wiederverbindung fehlgeschlagen, warte...")

    print("-----------------------------")
    time.sleep(2) # Sende alle 2 Sekunden (wie im Original)