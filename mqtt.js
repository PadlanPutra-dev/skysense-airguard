require("dotenv").config();
const mqtt = require("mqtt");

module.exports = function (io) {
    let latestData = null;

    const client = mqtt.connect({
        host: process.env.MQTT_HOST,
        port: process.env.MQTT_PORT
    });

    client.on("connect", () => {
        console.log("MQTT Connected");
        client.subscribe(process.env.MQTT_TOPIC);
    });

    client.on("message", (topic, message) => {
        const data = JSON.parse(message.toString());

        latestData = {
            suhu: data.temperature,
            kelembapan: data.humidity,
            arahangin: data.windDirection,
            kecepatan_angin: data.windSpeed,
            curah_hujan: data.rainRate,
            intensitas_cahaya: data.light
        };

        // KIRIM KE FRONTEND
        io.emit("mqttData", latestData);
    });
};
