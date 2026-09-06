// ==========================================================
// CONFIG
// ==========================================================

const API_URL = "http://127.0.0.1:8000";

let predictionChart = null;


// ==========================================================
// PARAMETER CONFIG
// ==========================================================

const PARAMETER_CONFIG = {

    temperature: {
        labels: [
            "TN",
            "TAVG",
            "TX"
        ],
        fields: [
            "TN",
            "TAVG",
            "TX"
        ],
        unit: "°C",
        title: "Suhu"
    },

    humidity: {
        labels: [
            "RH_AVG"
        ],
        fields: [
            "RH_AVG"
        ],
        unit: "%",
        title: "Kelembapan"
    },

    rain: {
        labels: [
            "RR"
        ],
        fields: [
            "RR"
        ],
        unit: "mm",
        title: "Curah Hujan"
    },

    sunshine: {
        labels: [
            "SS"
        ],
        fields: [
            "SS"
        ],
        unit: "jam",
        title: "Penyinaran Matahari"
    },

    wind: {
        labels: [
            "FF_AVG",
            "FF_X"
        ],
        fields: [
            "FF_AVG",
            "FF_X"
        ],
        unit: "",
        title: "Kecepatan Angin"
    }

};


// ==========================================================
// LOAD PREDICTION
// ==========================================================

async function loadPrediction(days) {

    const status =
        document.getElementById(
            "statusPrediksi"
        );


    const table =
        document.getElementById(
            "predictionTable"
        );


    try {


        // --------------------------------------------------
        // LOADING
        // --------------------------------------------------

        status.innerHTML =
            `Mengambil prediksi ${days} hari dari model...`;

        status.style.background =
            "#eff6ff";

        status.style.color =
            "#2563eb";


        table.innerHTML = `
            <tr>
                <td
                    colspan="9"
                    style="
                        text-align:center;
                        padding:20px;
                    "
                >
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
        // API ERROR
        // --------------------------------------------------

        if (data.error) {

            throw new Error(
                data.detail ||
                data.error
            );

        }


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
        // DATE INFORMATION
        // --------------------------------------------------

        const lastDataDate =
            data.last_data_date
                ? formatDate(data.last_data_date)
                : "-";


        const firstForecastDate =
            data.first_forecast_date
                ? formatDate(data.first_forecast_date)
                : "-";


        const lastForecastDate =
            data.last_forecast_date
                ? formatDate(data.last_forecast_date)
                : "-";


        // --------------------------------------------------
        // STATUS SUCCESS
        // --------------------------------------------------

        status.innerHTML = `
            <strong>
                Prediksi ${forecast.length} hari berhasil dimuat
            </strong>
            <br>
            Data terakhir:
            ${lastDataDate}
            <br>
            Periode prediksi:
            ${firstForecastDate}
            - ${lastForecastDate}
            <br>
            Sumber:
            ${escapeHTML(data.source || "Unknown")}
        `;


        status.style.background =
            "#ecfdf5";

        status.style.color =
            "#16a34a";


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

        status.innerHTML = `
            <strong>
                Gagal mengambil data prediksi.
            </strong>
            <br>
            ${escapeHTML(error.message)}
            <br>
            <small>
                Pastikan FastAPI berjalan di
                ${escapeHTML(API_URL)}
            </small>
        `;


        status.style.background =
            "#fee2e2";

        status.style.color =
            "#dc2626";


        // --------------------------------------------------
        // ERROR TABLE
        // --------------------------------------------------

        table.innerHTML = `
            <tr>
                <td
                    colspan="9"
                    style="
                        text-align:center;
                        padding:20px;
                        color:#dc2626;
                    "
                >
                    Gagal mengambil data prediksi.
                </td>
            </tr>
        `;

    }

}


// ==========================================================
// CREATE CHART
// ==========================================================

function createPredictionChart(
    forecast
) {


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
    // PARAMETER SELECTED
    // ------------------------------------------------------

    const parameterElement =
        document.getElementById(
            "parameter"
        );


    const selectedParameter =
        parameterElement
            ? parameterElement.value
            : "temperature";


    const config =
        PARAMETER_CONFIG[
            selectedParameter
        ];


    // ------------------------------------------------------
    // LABELS
    // ------------------------------------------------------

    const labels =
        forecast.map(
            item =>
                formatDate(
                    item.TANGGAL
                )
        );


    // ------------------------------------------------------
    // DATASET
    // ------------------------------------------------------

    const datasets =
        config.fields.map(
            (field, index) => {

                const datasetData =
                    forecast.map(
                        item => {

                            const value =
                                Number(
                                    item[field]
                                );

                            return Number.isFinite(value)
                                ? value
                                : null;

                        }
                    );


                const colors = [
                    "#3b82f6",
                    "#22c55e",
                    "#ef4444"
                ];


                return {

                    label:
                        config.labels[index],

                    data:
                        datasetData,

                    borderColor:
                        colors[index % colors.length],

                    backgroundColor:
                        colors[index % colors.length],

                    borderWidth:
                        index === 1
                            ? 3
                            : 2,

                    pointRadius:
                        forecast.length > 30
                            ? 0
                            : 3,

                    pointHoverRadius:
                        5,

                    tension:
                        0.35,

                    fill:
                        false

                };

            }
        );


    // ------------------------------------------------------
    // CHART
    // ------------------------------------------------------

    predictionChart =
        new Chart(
            ctx,
            {

                type:
                    "line",


                data: {

                    labels:
                        labels,

                    datasets:
                        datasets

                },


                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,


                    interaction: {

                        intersect:
                            false,

                        mode:
                            "index"

                    },


                    plugins: {

                        legend: {

                            display:
                                true,

                            position:
                                "top"

                        },


                        title: {

                            display:
                                true,

                            text:
                                `Prediksi ${config.title}`

                        },


                        tooltip: {

                            enabled:
                                true,


                            callbacks: {

                                label:
                                    function(context) {

                                        const value =
                                            Number(
                                                context.parsed.y
                                            );


                                        const formatted =
                                            Number.isFinite(value)
                                                ? value.toFixed(2)
                                                : "-";


                                        const unit =
                                            config.unit
                                                ? ` ${config.unit}`
                                                : "";


                                        return (
                                            context.dataset.label +
                                            ": " +
                                            formatted +
                                            unit
                                        );

                                    }

                            }

                        }

                    },


                    scales: {

                        x: {

                            title: {

                                display:
                                    true,

                                text:
                                    "Tanggal"

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

                                display:
                                    true,

                                text:
                                    config.unit
                                        ? `${config.title} (${config.unit})`
                                        : config.title

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

function createPredictionTable(
    forecast
) {


    const table =
        document.getElementById(
            "predictionTable"
        );


    table.innerHTML = "";


    forecast.forEach(
        item => {


            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${formatDate(item.TANGGAL)}
                </td>

                <td>
                    ${formatNumber(item.TN)}
                    °C
                </td>

                <td>
                    ${formatNumber(item.TX)}
                    °C
                </td>

                <td>
                    ${formatNumber(item.TAVG)}
                    °C
                </td>

                <td>
                    ${formatNumber(item.RH_AVG)}
                    %
                </td>

                <td>
                    ${formatNumber(item.RR)}
                    mm
                </td>

                <td>
                    ${formatNumber(item.SS)}
                    jam
                </td>

                <td>
                    ${formatNumber(item.FF_X)}
                </td>

                <td>
                    ${formatNumber(item.FF_AVG)}
                </td>

            `;


            table.appendChild(
                row
            );

        }
    );

}


// ==========================================================
// FORMAT NUMBER
// ==========================================================

function formatNumber(
    value
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "-";

    }


    return number.toFixed(2);

}


// ==========================================================
// FORMAT DATE
// ==========================================================

function formatDate(
    dateString
) {


    if (
        !dateString
    ) {

        return "-";

    }


    const date =
        new Date(
            `${dateString}T00:00:00`
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return dateString;

    }


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
// ESCAPE HTML
// ==========================================================

function escapeHTML(
    value
) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
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


        const parameter =
            document.getElementById(
                "parameter"
            );


        if (!periode) {

            console.error(
                "Element #periode tidak ditemukan."
            );

            return;

        }


        // --------------------------------------------------
        // INITIAL LOAD
        // --------------------------------------------------

        const initialDays =
            Number(
                periode.value
            );


        loadPrediction(
            initialDays
        );


        // --------------------------------------------------
        // PERIOD CHANGE
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


        // --------------------------------------------------
        // PARAMETER CHANGE
        // --------------------------------------------------

        if (parameter) {

            parameter.addEventListener(
                "change",
                function() {

                    console.log(
                        "Parameter berubah:",
                        this.value
                    );


                    loadPrediction(
                        Number(
                            periode.value
                        )
                    );

                }
            );

        }

    }
);