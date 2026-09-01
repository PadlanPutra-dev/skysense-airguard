// ==========================================================
// CONFIG
// ==========================================================

const API_URL = "http://127.0.0.1:8000";

let predictionChart = null;


// ==========================================================
// LOAD PREDICTION
// ==========================================================

async function loadPrediction(days) {

    const status =
        document.getElementById("statusPrediksi");

    const table =
        document.getElementById("predictionTable");


    try {

        // --------------------------------------------------
        // LOADING
        // --------------------------------------------------

        status.textContent =
            `Mengambil prediksi ${days} hari dari model...`;

        status.style.background = "#eff6ff";
        status.style.color = "#2563eb";


        table.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center;padding:20px;">
                    Memuat data prediksi...
                </td>
            </tr>
        `;


        // --------------------------------------------------
        // API URL
        // --------------------------------------------------

        const url =
            `${API_URL}/forecast?days=${days}`;


        console.log(
            "Request API:",
            url
        );


        // --------------------------------------------------
        // REQUEST
        // --------------------------------------------------

        const response =
            await fetch(url);


        // --------------------------------------------------
        // CHECK RESPONSE
        // --------------------------------------------------

        if (!response.ok) {

            throw new Error(
                `HTTP Error ${response.status}`
            );

        }


        // --------------------------------------------------
        // JSON
        // --------------------------------------------------

        const data =
            await response.json();


        console.log(
            "Data prediksi:",
            data
        );


        // --------------------------------------------------
        // VALIDATION
        // --------------------------------------------------

        if (
            !data.forecast ||
            data.forecast.length === 0
        ) {

            throw new Error(
                "Data forecast kosong."
            );

        }


        const forecast =
            data.forecast;


        console.log(
            `Jumlah forecast: ${forecast.length}`
        );


        // --------------------------------------------------
        // STATUS SUCCESS
        // --------------------------------------------------

        status.textContent =
            `Prediksi ${forecast.length} hari berhasil dimuat. Sumber: ${data.source}`;

        status.style.background = "#ecfdf5";
        status.style.color = "#16a34a";


        // --------------------------------------------------
        // UPDATE CHART
        // --------------------------------------------------

        createPredictionChart(
            forecast
        );


        // --------------------------------------------------
        // UPDATE TABLE
        // --------------------------------------------------

        createPredictionTable(
            forecast
        );


    } catch (error) {

        console.error(
            "Prediction Error:",
            error
        );


        // --------------------------------------------------
        // ERROR STATUS
        // --------------------------------------------------

        status.textContent =
            "Gagal mengambil data prediksi dari FastAPI.";

        status.style.background = "#fee2e2";
        status.style.color = "#dc2626";


        // --------------------------------------------------
        // ERROR TABLE
        // --------------------------------------------------

        table.innerHTML = `
            <tr>
                <td
                    colspan="5"
                    style="
                        text-align:center;
                        padding:20px;
                        color:#dc2626;
                    "
                >
                    Gagal mengambil data prediksi.
                    <br>
                    <small>
                        Pastikan FastAPI sedang berjalan di
                        ${API_URL}
                    </small>
                </td>
            </tr>
        `;

    }

}


// ==========================================================
// CREATE CHART
// ==========================================================

function createPredictionChart(forecast) {

    const canvas =
        document.getElementById(
            "chartPrediksi"
        );


    if (!canvas) {

        console.error(
            "Canvas chartPrediksi tidak ditemukan."
        );

        return;

    }


    const ctx =
        canvas.getContext("2d");


    // ------------------------------------------------------
    // DESTROY OLD CHART
    // ------------------------------------------------------

    if (predictionChart) {

        predictionChart.destroy();

        predictionChart = null;

    }


    // ------------------------------------------------------
    // LABELS
    // ------------------------------------------------------

    const labels =
        forecast.map(
            item => formatDate(item.TANGGAL)
        );


    // ------------------------------------------------------
    // DATA
    // ------------------------------------------------------

    const tn =
        forecast.map(
            item => Number(item.TN)
        );


    const tavg =
        forecast.map(
            item => Number(item.TAVG)
        );


    const tx =
        forecast.map(
            item => Number(item.TX)
        );


    // ------------------------------------------------------
    // CHART
    // ------------------------------------------------------

    predictionChart =
        new Chart(
            ctx,
            {

                type: "line",


                data: {

                    labels: labels,


                    datasets: [

                        {

                            label: "TN",

                            data: tn,

                            borderColor: "#3b82f6",

                            backgroundColor:
                                "rgba(59,130,246,0.1)",

                            borderWidth: 2,

                            pointRadius:
                                forecast.length > 30
                                    ? 0
                                    : 3,

                            pointHoverRadius: 5,

                            tension: 0.35,

                            fill: false

                        },


                        {

                            label: "TAVG",

                            data: tavg,

                            borderColor: "#22c55e",

                            backgroundColor:
                                "rgba(34,197,94,0.1)",

                            borderWidth: 3,

                            pointRadius:
                                forecast.length > 30
                                    ? 0
                                    : 3,

                            pointHoverRadius: 5,

                            tension: 0.35,

                            fill: false

                        },


                        {

                            label: "TX",

                            data: tx,

                            borderColor: "#ef4444",

                            backgroundColor:
                                "rgba(239,68,68,0.1)",

                            borderWidth: 2,

                            pointRadius:
                                forecast.length > 30
                                    ? 0
                                    : 3,

                            pointHoverRadius: 5,

                            tension: 0.35,

                            fill: false

                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,


                    interaction: {

                        intersect: false,

                        mode: "index"

                    },


                    plugins: {

                        legend: {

                            display: true,

                            position: "top"

                        },


                        tooltip: {

                            enabled: true,


                            callbacks: {

                                label:
                                    function(context) {

                                        return (
                                            context.dataset.label +
                                            ": " +
                                            Number(
                                                context.parsed.y
                                            ).toFixed(2) +
                                            " °C"
                                        );

                                    }

                            }

                        }

                    },


                    scales: {

                        x: {

                            title: {

                                display: true,

                                text: "Tanggal"

                            },


                            ticks: {

                                maxTicksLimit:
                                    forecast.length > 365
                                        ? 15
                                        : forecast.length > 30
                                            ? 15
                                            : 10

                            }

                        },


                        y: {

                            title: {

                                display: true,

                                text: "Suhu (°C)"

                            }

                        }

                    }

                }

            }
        );

}


// ==========================================================
// CREATE TABLE
// ==========================================================

function createPredictionTable(forecast) {

    const table =
        document.getElementById(
            "predictionTable"
        );


    table.innerHTML = "";


    forecast.forEach(
        item => {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${formatDate(item.TANGGAL)}
                </td>

                <td>
                    ${Number(item.TN).toFixed(2)} °C
                </td>

                <td>
                    ${Number(item.TX).toFixed(2)} °C
                </td>

                <td>
                    ${Number(item.TAVG).toFixed(2)} °C
                </td>

                <td>
                    ${Number(item.RH_AVG).toFixed(2)} %
                </td>

            `;


            table.appendChild(row);

        }
    );

}


// ==========================================================
// FORMAT DATE
// ==========================================================

function formatDate(dateString) {

    const date =
        new Date(
            dateString + "T00:00:00"
        );


    return date.toLocaleDateString(
        "id-ID",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );

}


// ==========================================================
// PERIOD CHANGE
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const periode =
            document.getElementById(
                "periode"
            );


        if (!periode) {

            console.error(
                "Element #periode tidak ditemukan."
            );

            return;

        }


        // --------------------------------------------------
        // DEFAULT
        // --------------------------------------------------

        const initialDays =
            Number(
                periode.value
            );


        loadPrediction(
            initialDays
        );


        // --------------------------------------------------
        // CHANGE
        // --------------------------------------------------

        periode.addEventListener(
            "change",
            function() {

                const days =
                    Number(
                        this.value
                    );


                console.log(
                    "Periode berubah:",
                    days,
                    "hari"
                );


                loadPrediction(
                    days
                );

            }
        );

    }
);