document.addEventListener('DOMContentLoaded', function() {
    console.log('Visualization page loaded');

    // Helper function to toggle no data message
    function toggleNoData(elementId, hasData) {
        const element = document.getElementById(elementId);
        if (hasData) {
            element.style.display = 'none';
        } else {
            element.style.display = 'block';
        }
    }

    // === Sentiment Analysis Chart ===
        const sentimentChartElement = document.getElementById('sentimentChart');
    const sentimentDataRaw = sentimentChartElement.dataset.chart || '{}';
    console.log("Raw Sentiment Data:", sentimentDataRaw);

    let sentimentData = {};
    try {
        sentimentData = JSON.parse(sentimentDataRaw);
    } catch (error) {
        console.error("❌ Failed to parse Sentiment Data:", error.message);
    }

    // === 判断是否有数据 ===
    if (Object.keys(sentimentData).length === 0 || !sentimentData.sentiment) {
        console.warn("⚠️ No sentiment data found. Showing 'No Data Uploaded'.");
        document.getElementById('noDataSentiment').style.display = 'block';
        document.getElementById('sentimentChart').style.display = 'none';
    } else {
        document.getElementById('noDataSentiment').style.display = 'none';
        document.getElementById('sentimentChart').style.display = 'block';

        // === 渲染 Chart ===
        const ctxSentiment = document.getElementById('sentimentChart').getContext('2d');
        
        new Chart(ctxSentiment, {
            type: 'pie',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [
                        (sentimentData.positive_score * 100).toFixed(1), 
                        (sentimentData.neutral_score * 100).toFixed(1), 
                        (sentimentData.negative_score * 100).toFixed(1)
                    ],
                    backgroundColor: ['#4CAF50', '#FFC107', '#F44336'],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverBorderColor: '#000000'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: function(tooltipItem) {
                                const label = tooltipItem.label;
                                const value = tooltipItem.raw;
                                return `${label}: ${value}%`;
                            }
                        }
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                animation: {
                    animateScale: true
                }
            }
        });
    }

    // === One-Word Analysis Chart ===
    const ngramData1 = JSON.parse(document.getElementById('ngramChart1').dataset.chart || '[]');
    toggleNoData('noDataNgram1', ngramData1.length > 0);

    if (ngramData1.length > 0) {
        const labels1 = ngramData1.map(item => item.ngram);
        const values1 = ngramData1.map(item => item.count);

        const ctxNgram1 = document.getElementById('ngramChart1').getContext('2d');
        new Chart(ctxNgram1, {
            type: 'bar',
            data: {
                labels: labels1,
                datasets: [{
                    label: 'One-Word Frequency',
                    data: values1,
                    backgroundColor: '#2196F3',
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // === Two-Word Analysis Chart ===
    const ngramData2 = JSON.parse(document.getElementById('ngramChart2').dataset.chart || '[]');
    toggleNoData('noDataNgram2', ngramData2.length > 0);

    if (ngramData2.length > 0) {
        const labels2 = ngramData2.map(item => item.ngram);
        const values2 = ngramData2.map(item => item.count);

        const ctxNgram2 = document.getElementById('ngramChart2').getContext('2d');
        new Chart(ctxNgram2, {
            type: 'bar',
            data: {
                labels: labels2,
                datasets: [{
                    label: 'Two-Word Frequency',
                    data: values2,
                    backgroundColor: '#4CAF50',
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // === Three-Word Analysis Chart ===
    const ngramData3 = JSON.parse(document.getElementById('ngramChart3').dataset.chart || '[]');
    toggleNoData('noDataNgram3', ngramData3.length > 0);

    if (ngramData3.length > 0) {
        const labels3 = ngramData3.map(item => item.ngram);
        const values3 = ngramData3.map(item => item.count);

        const ctxNgram3 = document.getElementById('ngramChart3').getContext('2d');
        new Chart(ctxNgram3, {
            type: 'bar',
            data: {
                labels: labels3,
                datasets: [{
                    label: 'Three-Word Frequency',
                    data: values3,
                    backgroundColor: '#FF9800',
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // === Word Cloud Analysis ===
    const wordFrequencyElement = document.getElementById('wordFrequencyChart');
    
    if (!wordFrequencyElement) {
        console.error("⚠️ Element with ID 'wordFrequencyChart' not found in DOM.");
    } else {
        const wordFreqDataRaw = wordFrequencyElement.dataset.chart;
        console.log("Raw Word Frequency Data:", wordFreqDataRaw);

        if (!wordFreqDataRaw || wordFreqDataRaw === "undefined") {
            console.error("❌ Error: Data is undefined or not set. Cannot parse JSON.");
            return;
        }

        let wordFreqData = [];
        try {
            const parsedData = JSON.parse(wordFreqDataRaw);

            if (parsedData.top_words) {
                wordFreqData = parsedData.top_words;
            } else {
                console.error("❌ Error: No 'top_words' found in parsed data.");
                return;
            }
        } catch (error) {
            console.error("❌ Failed to parse Word Frequency Data:", error.message);
            return;
        }

        // === If the data is empty, rendering is not performed ===
        if (wordFreqData.length === 0) {
            console.warn("⚠️ No word frequency data found. Skipping WordCloud rendering.");
            return;
        }

        // Data cleaning - Only retain non-symbolic words
        const VALID_WORD_REGEX = /^[a-zA-Z0-9]+$/;
        wordFreqData = wordFreqData.filter(item => VALID_WORD_REGEX.test(item.word));

        // The data required for generating the word cloud
        const wordList = wordFreqData.map(item => [item.word, item.count]);

        // ===Rendering word cloud===
        const container = document.getElementById('wordCloudContainer');
        document.getElementById('heading5').addEventListener('click', () => {
            setTimeout(() => {
                console.log("✅ Word Cloud 正在渲染...");
                container.innerHTML = ""; // Clear the previous content
                WordCloud(container, {
                    list: wordList,
                    gridSize: Math.round(16 * container.clientWidth / 1024),
                    weightFactor: (size) => Math.log2(size + 2) * 15,  // Adjust the font size
                    fontFamily: 'Times, serif',
                    color: () => {
                        return '#' + Math.floor(Math.random() * 16777215).toString(16);
                    },
                    backgroundColor: '#ffffff',
                    rotateRatio: 0.3,  // Reduce rotation
                    rotationSteps: 2,
                    shuffle: true,
                    drawOutOfBound: true,
                    click: function(item, dimension, event) {
                        alert(`The word you clicked is: ${item[0]}, frequency: ${item[1]}`);
                    }
                });
            }, 500); // Wait for high loading with a delay of 500ms
        });

        // Trigger a click to ensure the initial loading display
        document.getElementById('heading5').click();
    }


    // === Named Entity Recognition Display ===
    const nerDataRaw = document.getElementById('nerList').dataset.chart || '{}';
    console.log("Raw NER Data:", nerDataRaw);

    const nerData = JSON.parse(nerDataRaw);
    toggleNoData('noDataNER', Object.keys(nerData).length > 0);

    if (Object.keys(nerData).length > 0) {
        const nerList = document.getElementById('nerList');
        for (const [entityType, entities] of Object.entries(nerData)) {
            const listItem = document.createElement('li');
            const entityNames = entities.map(entity => entity.text).join(", ");
            listItem.textContent = `${entityType}: ${entityNames}`;
            nerList.appendChild(listItem);
        }
    }

    

});