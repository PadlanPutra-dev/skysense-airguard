require("dotenv").config();
const express = require("express");
const cors = require("cors");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(cors());
app.use(express.json());

// PENTING: kirim io ke MQTT
require("./mqtt")(io);

// API sensor
const sensorRoute = require("./routes/sensorRoute");
app.use("/api/sensor", sensorRoute);

const predictionRoute = require("./routes/predictionRoute");
app.use("/api/prediction", predictionRoute);

// STATIC FILE
app.use(express.static("public"));

// CAMERA ROUTE
const cameraRoute = require("./routes/cameraRoute");
app.use("/api", cameraRoute);

// CAMERA PAGE
app.get("/camera", (req, res) => {
    res.sendFile(__dirname + "/public/camera.html");
});

// SOCKET CONNECTION
io.on("connection", (socket) => {
    console.log("Browser connected:", socket.id);
});

// START SERVER
server.listen(process.env.PORT, () => {
    console.log("Server running on port", process.env.PORT);
});
