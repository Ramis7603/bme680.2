import paho.mqtt.client as mqtt
import mariadb
import sys

# MariaDB-Verbindungsdaten anpassen
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "54tzck23"
DB_NAME = "mqtt_data"

# MQTT-Broker Daten
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SUB = "test/topic/in"
MQTT_TOPIC_PUB = "test/topic/out"

# Verbindung zur MariaDB herstellen
def connect_db():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            database=DB_NAME
        )
        return conn
    except mariadb.Error as e:
        print(f"Fehler bei DB-Verbindung: {e}")
        sys.exit(1)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Verbindung erfolgreich")
        client.subscribe("test/topic")
        print(f"Subscribed auf Topic: {MQTT_TOPIC_SUB}")
    else:
        print(f"Verbindung fehlgeschlagen mit Code {rc}")

def on_message(client, userdata, msg):
    print(f"Nachricht empfangen auf {msg.topic}: {msg.payload.decode()}")

    # In DB speichern
    try:
        conn = userdata['db_conn']
        cursor = conn.cursor()
        sql = "INSERT INTO mqtt_messages (topic, message) VALUES (?, ?)"
        cursor.execute(sql, (msg.topic, msg.payload.decode()))
        conn.commit()
        print("Nachricht in MariaDB gespeichert.")
        print("--------------------------------------")
    except mariadb.Error as e:
        print(f"DB Fehler: {e}")

def main():
    # DB-Verbindung aufbauen
    db_conn = connect_db()

    # MQTT Client einrichten
    client = mqtt.Client(userdata={'db_conn': db_conn})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Nachrichten veröffentlichen (z.B. testnachricht)
    client.loop_start()
    client.publish(MQTT_TOPIC_PUB, "Hallo von Raspberry Pi!")
    print(f"Nachricht gesendet auf {MQTT_TOPIC_PUB}")

    # Endlosschleife, um Nachrichten zu empfangen
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Programm beendet")
    finally:
        client.loop_stop()
        db_conn.close()

if __name__ == "__main__":
    main()
