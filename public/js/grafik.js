function createChart(id,label,color){

new Chart(document.getElementById(id),{

type:'line',

data:{
labels:["08:00","09:00","10:00","11:00","12:00","13:00"],

datasets:[{
label:label,
data:[
Math.random()*30,
Math.random()*30,
Math.random()*30,
Math.random()*30,
Math.random()*30,
Math.random()*30
],
borderColor:color,
backgroundColor:color,
tension:0.4,
fill:false
}]

},

options:{
responsive:true,
maintainAspectRatio:false
}

})

}

createChart("chartTemp","Suhu (°C)","red")
createChart("chartHumidity","Humidity (%)","blue")
createChart("chartWind","Wind (m/s)","green")
createChart("chartRain","Rain (mm)","orange")
createChart("chartLight","Light (lux)","purple")