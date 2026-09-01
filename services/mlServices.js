const axios = require("axios");

const ML_API = "http://127.0.0.1:8000/predict";

async function predictWeather(history) {
    try {

        const response = await axios.post(ML_API, {
            history
        });

        return response.data.prediction;

    } catch (err) {

        console.error("ML API Error");

        if (err.response) {
            console.error(err.response.data);
        } else {
            console.error(err.message);
        }

        throw err;
    }
}

module.exports = predictWeather;