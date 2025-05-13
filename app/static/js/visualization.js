document.addEventListener('DOMContentLoaded', function() {
    console.log('Visualization page loaded - SIMPLIFIED VERSION');

    // SENTIMENT CHART
    try {
        const sentimentChart = document.getElementById('sentimentChart');
        if (sentimentChart) {
            console.log('Found sentiment chart element');
            const sentimentData = JSON.parse(sentimentChart.getAttribute('data-chart') || '{}');
            
            if (sentimentData && sentimentData.positive_score) {
                console.log('Rendering sentiment chart with data:', sentimentData);
                
                const ctx = sentimentChart.getContext('2d');
                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: ['Positive', 'Neutral', 'Negative'],
                        datasets: [{
                            data: [
                                (sentimentData.positive_score * 100).toFixed(1),
                                (sentimentData.neutral_score * 100).toFixed(1),
                                (sentimentData.negative_score * 100).toFixed(1)
                            ],
                            backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
                        }]
                    },
                    options: {
                        responsive: true
                    }
                });
            } else {
                console.warn('No valid sentiment data found');
            }
        } else {
            console.error('Sentiment chart element not found');
        }
    } catch (error) {
        console.error('Error rendering sentiment chart:', error);
    }

    // NGRAM CHARTS
    try {
        const ngramIds = ['ngramChart1', 'ngramChart2', 'ngramChart3'];
        const colors = ['#2196F3', '#4CAF50', '#FF9800'];
        const titles = ['One-Word Frequency', 'Two-Word Frequency', 'Three-Word Frequency'];

        ngramIds.forEach((id, index) => {
            const ngramChart = document.getElementById(id);
            if (ngramChart) {
                console.log(`Found ${id} element`);
                const ngramData = JSON.parse(ngramChart.getAttribute('data-chart') || '[]');
                
                if (ngramData && ngramData.length > 0) {
                    console.log(`Rendering ${id} with ${ngramData.length} items`);
                    
                    const labels = ngramData.map(item => item.ngram);
                    const values = ngramData.map(item => item.count);
                    
                    const ctx = ngramChart.getContext('2d');
                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels.slice(0, 10), // Limit to top 10 for better display
                            datasets: [{
                                label: titles[index],
                                data: values.slice(0, 10),
                                backgroundColor: colors[index]
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                } else {
                    console.warn(`No valid data for ${id}`);
                }
            } else {
                console.error(`${id} element not found`);
            }
        });
    } catch (error) {
        console.error('Error rendering ngram charts:', error);
    }

    // WORD CLOUD
    try {
        const wordFreqChart = document.getElementById('wordFrequencyChart');
        const wordCloudContainer = document.getElementById('wordCloudContainer');
        
        if (wordFreqChart && wordCloudContainer) {
            console.log('Found word cloud elements');
            
            const wordFreqData = JSON.parse(wordFreqChart.getAttribute('data-chart') || '{}');
            if (wordFreqData && wordFreqData.top_words && wordFreqData.top_words.length > 0) {
                console.log(`Found ${wordFreqData.top_words.length} words for word cloud`);
                
                const wordList = wordFreqData.top_words
                    .filter(item => /^[a-zA-Z0-9]+$/.test(item.word))
                    .map(item => [item.word, item.count]);
                
                console.log('Rendering word cloud with data:', wordList.slice(0, 5));
                
                // Clear any previous content
                wordCloudContainer.innerHTML = '';
                
                // Render word cloud with a slight delay to ensure container is ready
                setTimeout(() => {
                    WordCloud(wordCloudContainer, {
                        list: wordList,
                        gridSize: 16,
                        weightFactor: 10,
                        fontFamily: 'Arial',
                        color: () => {
                            return '#' + Math.floor(Math.random() * 16777215).toString(16);
                        },
                        backgroundColor: '#ffffff'
                    });
                    console.log('Word cloud rendered');
                }, 300);
            } else {
                console.warn('No valid word data for word cloud');
                wordCloudContainer.textContent = 'No word data available for visualization';
            }
        } else {
            console.error('Word cloud elements not found');
        }
    } catch (error) {
        console.error('Error rendering word cloud:', error);
    }

    // Auto-open all accordion sections after a delay
    setTimeout(() => {
        document.querySelectorAll('.accordion-button').forEach(button => {
            if (button.classList.contains('collapsed')) {
                button.click();
            }
        });
    }, 500);
});