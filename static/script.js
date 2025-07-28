
fetch('/api/chart-data')
  .then(response => response.json())
  .then(data => {

    console.log("Values:", data.values)
    console.log("Timestamps: ", data.labels)
    let highestValue = 0
    let bcolor = "green"

    data.values.forEach(element => {
        if(element >= highestValue){
            highestValue = element
        }
    });


    if(data.values[0] >= data.values[data.values.length-1]){
        bcolor = "red";
    } else {
        bcolor = "green";
    }

    const ctx = document.getElementById('myChart').getContext('2d');

    new Chart(ctx, {
    type: "line",
    data: {
        labels: data.labels,
        datasets: [{
        borderColor: bcolor,
        data: data.values
        }]
    },
    options:{
        legend: {display: false},
        scales: {
            yAxes: [
                {
                    ticks: {
                        maxTicksLimits: 5,
                        min: 0,
                        max: highestValue + (highestValue * 0.2),
                        stepSize: (highestValue / 3),
                        display: true
                    }
                }
            ],
            xAxes: [{
                ticks: {
                    display: true // for dynamic control
                },
        
            }],
        }
    }
    });
  })
  .catch(err => console.error("Chart data load error:", err));



  function generalInfo() {
    fetch('/api/status')
      .then(response => response.json())
      .then(data => {
        document.getElementById('stock').textContent = data.stock;
        document.getElementById('accountValue').textContent = data.accountValue;
        document.getElementById('purchaseDate').textContent = " " + data.purchaseDate;
      });
  }

  // Run once on page load and every 60 seconds
  generalInfo();
  setInterval(generalInfo, 30000);

function running(value) {
    fetch('/toggle-running', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ running: value === 'True' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Reload page to reflect the new state
        }
    });
}

function togglePiView() {
    const PiView = document.getElementById("PiViewElement");
    const WebView = document.getElementById("WebViewElement");
    const welcome = document.getElementById("welcomeHdr");

    PiView.style.display = (PiView.style.display === "none") ? "block" : "none";

    if(WebView.getAttribute("hidden") !== null){
        WebView.removeAttribute("hidden");
        toggleAxisTicks();
    } else {
        WebView.setAttribute("hidden", "");
        toggleAxisTicks();
    }


  // Safely toggle or show it
  if (welcome) {
    welcome.hidden = !welcome.hidden;
  }
}

function toggleAxisTicks() {
  const currenty = myChart.options.scales.yAxes[0].ticks.display;
  myChart.options.scales.yAxes[0].ticks.display = !currenty; 
  
  const currentx = myChart.options.scales.xAxes[0].ticks.display;
  myChart.options.scales.xAxes[0].ticks.display = !currentx;
  
  // Toggle true/false
  myChart.update(); // Apply the change
}

function updateInfo() {
    const API_KEY = document.getElementById('u-api-key').value.trim();
    const SECRET_KEY = document.getElementById('u-secret-key').value.trim();
    const PAY_DATE = document.getElementById('u-pay-date').value.trim();

    fetch('/update-info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            API_KEY: API_KEY,
            SECRET_KEY: SECRET_KEY,
            PAY_DATE: PAY_DATE
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success == false) {
            const modalMsg = document.getElementById('modalErrorMsg2');

              if (modalMsg.hidden) {
                    modalMsg.hidden = !modalMsg.hidden;
                }

        } else {
            const modalMsg = document.getElementById('modalSuccessMsg2');

              if (modalMsg.hidden) {
                    modalMsg.hidden = !modalMsg.hidden;
                }

                setTimeout(function () {
                    location.reload();
                }, 1500);
  
            
        }
    });
}

function initialInfo() {
    const API_KEY = document.getElementById('i-api-key').value.trim();
    const SECRET_KEY = document.getElementById('i-secret-key').value.trim();
    const PAY_DATE = document.getElementById('i-pay-date').value.trim();
    const STOCK = document.getElementById('i-dropdown-input').value.trim();


    fetch('/initial-info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            API_KEY: API_KEY,
            SECRET_KEY: SECRET_KEY,
            PAY_DATE: PAY_DATE,
            STOCK: STOCK
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success == false) {
            const modalMsg = document.getElementById('modalErrorMsg');

              if (modalMsg.hidden) {
                    modalMsg.hidden = !modalMsg.hidden;
                }

        } else {
            const modalMsg = document.getElementById('modalSuccessMsg');

              if (modalMsg.hidden) {
                    modalMsg.hidden = !modalMsg.hidden;
                }

                setTimeout(function () {
                    location.reload();
                }, 1500);
  
            
        }
    });
}