async function fetchLatestData() {
    try {
        const res = await fetch("/api/sensor/latest");
        const d = await res.json();

        document.getElementById("temperature").innerText = d.suhu + " °C";
        document.getElementById("humidity").innerText = d.kelembapan + " %";
        document.getElementById("wind").innerText = d.kecepatan_angin + " m/s";
        document.getElementById("rainfall").innerText = d.curah_hujan + " mm";
        document.getElementById("light").innerText = d.intensitas_cahaya + " lux";

        checkAlert(d);
        updateChart(d);

    } catch (err) {
        console.log("Error Fetching:", err);
    }
}

async function loadHistory() {
    const res = await fetch("/api/sensor/history");
    const rows = await res.json();

    const table = document.getElementById("historyTable");
    table.innerHTML = "";

    function formatWaktu(dateString) {
        const d = new Date(dateString);
        return d.toLocaleDateString("id-ID") + " " + d.toLocaleTimeString("id-ID");
    }

    rows.forEach(r => {
        table.innerHTML += `
            <tr>
                <td>${formatWaktu(r.created_at)}</td>
                <td>${r.suhu}</td>
                <td>${r.kelembapan}</td>
                <td>${r.kecepatan_angin}</td>
                <td>${r.curah_hujan}</td>
                <td>${r.intensitas_cahaya}</td>
            </tr>
        `;
    });
}

function checkAlert(d) {
    const box = document.getElementById("alertBox");

    if (d.suhu > 35) {
        box.innerText = "⚠ Suhu melebihi batas!";
    } 
    else if (d.kelembapan > 85) {
        box.innerText = "⚠ Kelembapan sangat tinggi!";
    }
    else {
        box.innerText = "Tidak ada peringatan.";
    }
}

// CHART UNTUK SEMUA SENSOR
let chart;

document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById("sensorChart");

    if (!ctx) {
        console.error("Canvas sensorChart tidak ditemukan");
        return;
    }

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                { label: "Suhu (°C)", data: [], borderColor: "red", tension: 0.3 },
                { label: "Kelembapan (%)", data: [], borderColor: "blue", tension: 0.3 },
                { label: "Kecepatan Angin (m/s)", data: [], borderColor: "purple", tension: 0.3 },
                { label: "Curah Hujan (mm)", data: [], borderColor: "orange", tension: 0.3 },
                { label: "Cahaya (lux)", data: [], borderColor: "brown", tension: 0.3 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
 const socket = io();

    socket.on("mqttData", (d) => {
        if (!d) return;
        updateChart(d);
    });
    console.log("Chart berhasil dibuat");
});

function updateChart(d) {

    if (!chart || !d) return;
    console.log("Hello world");

    chart.data.labels.push(new Date().toLocaleTimeString());

    chart.data.datasets[0].data.push(+d.suhu);
    chart.data.datasets[1].data.push(+d.kelembapan);
    chart.data.datasets[2].data.push(+d.kecepatan_angin);
    chart.data.datasets[3].data.push(+d.curah_hujan);
    chart.data.datasets[4].data.push(+d.intensitas_cahaya);

    if (chart.data.labels.length > 20) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(ds => ds.data.shift());
    }

    chart.update();
}

// Function BMKG
// Function BMKG: Menampilkan semua data cuaca ke tabel
async function loadBMKG() {
    try {
        const api = "http://192.168.1.197:3000/avgdata";
        const res = await fetch(api);
        const data = await res.json();

        const table = document.getElementById("historyTable");
        if (!table) return;

        table.innerHTML = "";

        function formatWaktu(dateString) {
            const d = new Date(dateString);
            return d.toLocaleDateString("id-ID") + " " + d.toLocaleTimeString("id-ID");
        }

        // DATA ADALAH ARRAY OBJECT
        data.forEach(c => {
            table.innerHTML += `
                <tr>
                    <td>${formatWaktu(c.tanggal)}</td>
                    <td>${c.avg_temperature} °C</td>
                    <td>${c.avg_humidity} %</td>
                    <td>${c.avg_wind_speed} m/s</td>
                    <td>${c.max_temperature} °C</td>
                    <td>${c.min_temperature} °C</td>
                    <td>${c.avg_ldr}</td>
                </tr>
            `;
        });

    } catch (err) {
        console.error("Error loadBMKG:", err);
    }
}

const socket = io();

socket.on("mqttData", (d) => {
    // CEGAH DATA KOSONG
    if (!d) return;
     const now = new Date();
    const jam = now.toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });


        document.getElementById("currentTime").innerText = jam;

            document.getElementById("currentStatus").innerText = "Suhu Saat Ini";

document.getElementById("currentTemp").innerText =
    parseFloat(d.suhu).toFixed(2) + " °C";

document.getElementById("temperature").innerText =
    parseFloat(d.suhu).toFixed(2) + " °C";
    document.getElementById("humidity").innerText = d.kelembapan + " %";
    document.getElementById("arahangin").innerText = getWindDirectionText(d.arahangin )?? "--";
    document.getElementById("wind").innerText = d.kecepatan_angin + " m/s";
    document.getElementById("rainfall").innerText = d.curah_hujan + " mm";
    document.getElementById("light").innerText = d.intensitas_cahaya + " lux";

    // optional
    if (typeof checkAlert === "function") checkAlert(d);
    if (typeof updateChart === "function") updateChart(d);
});
function getWindDirectionText(degree) {
    if (degree == null) return "-";
    if (degree >= 337.5 || degree < 22.5) return "Utara";
    if (degree < 67.5) return "Timur Laut";
    if (degree < 112.5) return "Timur";
    if (degree < 157.5) return "Tenggara";
    if (degree < 202.5) return "Selatan";
    if (degree < 247.5) return "Barat Daya";
    if (degree < 292.5) return "Barat";
    return "Barat Laut";
}


// Panggil function langsung
loadBMKG();

// Jika ingin auto refresh setiap 2 detik
// setInterval(loadBMKG, 2000);


//setInterval(fetchLatestData, 2000);
//setInterval(loadHistory, 5000);
setInterval(loadBMKG, 2000);

//fetchLatestData();
//BMKGData();
loadBMKG();
//loadHistory();
