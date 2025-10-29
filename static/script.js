async function getPrediction() {
    // Gather input values from the form
    const age = document.getElementById('age').value;
    const sex = document.getElementById('sex').value;
    const cholesterol = document.getElementById('cholesterol').value;
    const maxhr = document.getElementById('maxhr').value;
    const oldpeak = document.getElementById('oldpeak').value;
    const exerciseangina = document.getElementById('exerciseangina').value;
    const chestpain = document.getElementById('chestpain').value;
    const st_slope = document.getElementById('st_slope').value;

    // Create a data object to send to the server
    const data = {
        Age: age, 
        Sex: sex,
        Cholesterol: cholesterol,
        MaxHR: maxhr,
        Oldpeak: oldpeak,
        ExerciseAngina: exerciseangina,
        ChestPainType: chestpain,
        ST_Slope: st_slope
    };

    try {
        // Make a POST request to the Flask backend
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        // Handle the response
        const result = await response.json();
        if (response.ok) {
            // Update the prediction result
            document.getElementById('predictionResult').innerText = result.prediction;

            // Visualize the risk score using a gauge chart
            visualizeRisk(result.risk_score);

            // Provide suggestions based on the risk
            provideSuggestions(result.prediction);
        } else {
            // Handle errors
            document.getElementById('predictionResult').innerText = 'Error: ' + result.error;
            document.getElementById('suggestions').innerText = '';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('predictionResult').innerText = 'Error: ' + error.message;
        document.getElementById('suggestions').innerText = '';
    }
}
let gaugeChart;
function visualizeRisk(riskScore) {
    const ctx = document.getElementById('gaugeChart').getContext('2d');

    // Destroy any existing chart instance to avoid conflicts
    if (gaugeChart) {
        gaugeChart.destroy();
    }

    // Create a new doughnut chart
    gaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Risk', 'Safe'],
            datasets: [{
                data: [riskScore * 100, (1 - riskScore) * 100], // Convert to percentage
                backgroundColor: ['#FF6384', '#36A2EB'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%', // Create a doughnut effect
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            return tooltipItem.label + ': ' + Math.round(tooltipItem.raw) + '%';
                        }
                    }
                }
            }
        }
    });
    
}


function provideSuggestions(prediction) {
    const suggestionsElement = document.getElementById('suggestions');
    
    if (prediction === "High Risk") {
        suggestionsElement.innerHTML = `
            <ul>
                <li>We recommend consulting a healthcare professional immediately.</li>
                <li>Maintain a healthy diet.</li>
                <li>Exercise regularly.</li>
            </ul>
        `;
    } else {
        suggestionsElement.innerHTML = `
            <ul>
                <li>Keep up your healthy habits.</li>
                <li>Regular check-ups are recommended.</li>
                <li>Stay active and engage in regular physical activity.</li>
            </ul>
        `;
    } 
     
}
