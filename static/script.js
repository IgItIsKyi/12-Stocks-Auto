
fetch('/api/chart-data')
  .then(response => response.json())
  .then(data => {

    console.log("Values:", data.values)
    console.log("Timestamps: ", data.labels)
    let highestValue = 0
    let bcolor = "green"

    let lowestValue = data.values[0]

    data.values.forEach(element => {
        if(element >= highestValue){
            highestValue = element
        }
        if(element <= lowestValue){
            lowestValue = element
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
                        max: highestValue + (highestValue * 0.2),
                        stepSize: (highestValue / 3),
                        min: lowestValue - (lowestValue * 0.2),
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

  function tableInfo(forceInitial = false) {
    fetch(`/api/logTable${forceInitial ? '?forceInitial=true' : ''}`)
      .then(response => response.json())
      .then(data => {
        var lastID  // Figure out what was the last ID used in the initial page load
        console.log("IntRun var: "+ data.initialRun)

        const logBody = document.getElementById('logInfo');
        if (!logBody) return;

        // Clear table if this is an initial run

      // Clear table if this is an initial run
      if (data.initialRun === true) {
        logBody.innerHTML = '';
        console.log("Initial run: rebuilding full log table");

        // Rebuild the full table
        const [ids, timestamps, messages] = data.logs;
        for (let i = 0; i < ids.length; i++) {
          const row = `
            <tr>
              <th scope="row">${ids[i]}</th>
              <td>${timestamps[i]}</td>
              <td>${messages[i]}</td>
            </tr>`;
          logBody.insertAdjacentHTML('beforeend', row);
        }

        // Keep track of last ID if needed for later updates
        window.lastID = ids[ids.length - 1];

      } else {
        console.log("Update run: appending new logs if any");

        // Append only new rows if any exist
        const [ids, timestamps, messages] = data.logs;
        if (typeof window.lastID === 'undefined') {
          window.lastID = 0;
        }

        for (let i = 0; i < ids.length; i++) {
          if (ids[i] > window.lastID) {
            const row = `
              <tr>
                <th scope="row">${ids[i]}</th>
                <td>${timestamps[i]}</td>
                <td>${messages[i]}</td>
              </tr>`;
            logBody.insertAdjacentHTML('beforeend', row);
            window.lastID = ids[i];
          }
        }
      }
    })

    .catch(err => console.error("Error loading log table:", err));


    }

function running(value) {
  console.log("Button value: ", value)
  fetch('/toggle-running', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ running: value })
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
        console.log("New state: ", data.is_running)
          // Force an initial log reload after refresh
          sessionStorage.setItem('forceInitialLogs', 'true');
          location.reload();
      }
  })
  .catch(err => console.error("Error toggling running state:", err));


}

function togglePiView() {
    const PiView = document.getElementById("PiViewElement");
    const PiView2 = document.getElementById("PiViewElement2");
    const WebView = document.getElementById("WebViewElement");
    const welcome = document.getElementById("welcomeHdr");

    PiView.style.display = (PiView.style.display === "none") ? "block" : "none";
    PiView2.style.display = (PiView2.style.display === "none") ? "block" : "none";

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
  const STOCK = document.getElementById('stockButton').textContent.trim();

  console.log("STOCK: ", STOCK)
  fetch('/update-info', {
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


function runUpdate() {
  fetch('/api/run-update')
    .then(response => response.json())
    .then(data => {
      document.getElementById('stock').textContent = data.stock;
      document.getElementById('accountValue').textContent = data.accountValue;
      document.getElementById('purchaseDate').textContent = " " + data.purchaseDate;

    });
}

window.addEventListener('load', () => {
  const forceInitial = sessionStorage.getItem('forceInitialLogs') === 'true';
  tableInfo(forceInitial);
  sessionStorage.removeItem('forceInitialLogs'); // clean it up

  generalInfo();
  setInterval(generalInfo, 30000);
  setInterval(() => tableInfo(false), 30000); // only fetch updates every 30s
});