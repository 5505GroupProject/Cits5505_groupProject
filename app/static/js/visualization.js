// Donut Chart for Sentiment Analysis
const ctx = document.getElementById('sentimentChart').getContext('2d');
const sentimentChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [{
            data: [40, 30, 30],
            backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'top' },
            tooltip: { enabled: true }
        }
    }
});

// Word Cloud
const words = [
    {text: 'news', size: 60},
    {text: 'sentiment', size: 50},
    {text: 'analysis', size: 40},
    {text: 'positive', size: 30},
    {text: 'negative', size: 25}
];

d3.layout.cloud().size([500, 400])
    .words(words)
    .padding(5)
    .rotate(() => ~~(Math.random() * 2) * 90)
    .fontSize(d => d.size)
    .on("end", draw)
    .start();

function draw(words) {
    d3.select("#wordCloud").append("svg")
        .attr("width", 500)
        .attr("height", 400)
        .append("g")
        .attr("transform", "translate(250,200)")
        .selectAll("text")
        .data(words)
        .enter().append("text")
        .style("font-size", d => `${d.size}px`)
        .style("fill", "#000")
        .attr("text-anchor", "middle")
        .attr("transform", d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
        .text(d => d.text);
}

// Share Button
document.getElementById('shareButton').addEventListener('click', function() {
    const modalBody = document.getElementById('shareModalBody');
    modalBody.innerHTML = ''; // Clear previous content
    const shareContent = document.getElementById('fullText').innerText;
    modalBody.innerHTML = `
        <p>Share this analysis: ${shareContent.substring(0, 100)}...</p>
        {% include 'share.html' %}
    `;
});