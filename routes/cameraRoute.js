const express = require("express");
const router = express.Router();
const db = require("../db");

// Fungsi rekomendasi otomatis
function generateRecommendation(suhu, kelembapan, hujan) {

    if (hujan > 5) return "Sedang hujan — sebaiknya di rumah saja.";
    if (suhu > 32) return "Cuaca panas — kurangi aktivitas luar ruangan.";
    if (kelembapan > 85) return "Kelembapan tinggi — hati-hati potensi hujan.";
    return "Cuaca cerah — aman untuk aktivitas luar.";
}

// API untuk rekomendasi
router.get("/recommend", (req, res) => {
    db.query("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1", (err, rows)=>{
        if(err) return res.json({error: err});

        const { suhu, kelembapan, curah_hujan } = rows[0];

        const rekom = generateRecommendation(suhu, kelembapan, curah_hujan);

        res.json({ 
            rekomendasi: rekom,
            suhu, kelembapan, curah_hujan
        });
    });
});

module.exports = router;
