const express = require("express");
const router = express.Router();
const db = require("../db");

// ==============================
// 1. POST data dari MQTT
// ==============================
router.post("/", (req, res) => {
    const { suhu, kelembapan } = req.body;

    if (!suhu || !kelembapan) {
        return res.status(400).json({ error: "Data tidak lengkap" });
    }

    const sql = "INSERT INTO sensor_data (suhu, kelembapan) VALUES (?, ?)";
    db.query(sql, [suhu, kelembapan], (err, result) => {
        if (err) {
            console.error("Error insert:", err);
            return res.status(500).json({ error: "Database error" });
        }
        res.json({ message: "Data berhasil disimpan" });
    });
});


// ==============================
// 2. GET data terbaru
// ==============================
router.get("/latest", (req, res) => {
    const sql = "SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1";
    db.query(sql, (err, rows) => {
        if (err) return res.json({ error: err });
        res.json(rows[0] || {});
    });
});


// ==============================
// 3. GET history untuk tabel & grafik
// ==============================
router.get("/history", (req, res) => {
    const sql = "SELECT * FROM sensor_data ORDER BY id DESC LIMIT 50";
    db.query(sql, (err, rows) => {
        if (err) return res.json({ error: err });
        res.json(rows);
    });
});


// ==============================
// 4. GET alert (suhu > 35 atau kelembapan > 85)
// ==============================
router.get("/alerts", (req, res) => {
    const sql = `
        SELECT * FROM sensor_data 
        WHERE suhu > 35 OR kelembapan > 85
        ORDER BY id DESC LIMIT 10
    `;
    db.query(sql, (err, rows) => {
        if (err) return res.json({ error: err });
        res.json(rows);
    });
});

// ==============================
// GET semua riwayat
// ==============================
router.get("/history-all", (req, res) => {
    const sql = "SELECT * FROM sensor_data ORDER BY id DESC";

    db.query(sql, (err, rows) => {
        if (err) return res.status(500).json({ error: err });
        res.json(rows);
    });
});

module.exports = router;
