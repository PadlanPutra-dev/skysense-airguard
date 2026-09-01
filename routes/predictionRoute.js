const express = require("express");
const axios = require("axios");

const router = express.Router();

const ML_API_URL = "http://127.0.0.1:8000";


// ==========================================================
// GET FORECAST 7 HARI
// ==========================================================

router.get("/forecast", async (req, res) => {

    try {

        const response = await axios.get(
            `${ML_API_URL}/predict/forecast`
        );

        res.json(response.data);

    } catch (error) {

        console.error(
            "Prediction API Error:",
            error.message
        );

        res.status(500).json({
            error: "Gagal mengambil data prediksi dari ML API"
        });

    }

});

module.exports = router;