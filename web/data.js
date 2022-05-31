  
  
window.onload = function(){
    econ();
}

// Call API
document.getElementById("btn-test").addEventListener("click", trade);

function econ() {
$.getJSON('http://localhost:8080/econ?symbol=ETHUSDT&interval=1d&num=1000', function(data){
    console.log('Calling API /econ.')
    // var display = `Datetime: ${data.date[0]}<br>
    //             Open: ${data.open[0]}<br>   
    //             High: ${data.high[0]}<br>
    //             Low: ${data.low[0]}<br>
    //             Close: ${data.close[0]}<br>`
    // $("#k-line").html(display);
    

    var trace1 = {

        x: Object.values(data.date),        
        close: Object.values(data.close),        
        decreasing: {line: {color: 'red'}}, 
        high: Object.values(data.high),        
        increasing: {line: {color: 'green'}}, 
        line: {color: 'black'}, 
        low: Object.values(data.low),        
        open: Object.values(data.open),        
        type: 'candlestick', 
        xaxis: 'x', 
        yaxis: 'y'

    };
      
    var datawrap = [trace1];
    
    var layout = {
        plot_bgcolor:"transparent",
        paper_bgcolor:"transparent",
        dragmode: 'zoom', 
        margin: {
            r: 25, 
            t: 25, 
            b: 40, 
            l: 35
        }, 
        showlegend: false, 
        
        xaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            range: [data.date[0], data.date[999]], 
            rangeslider: {visible: false}, 
            // title: 'Date', 
            type: 'date'
        }, 
        yaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            range: [Math.min(Object.values(data.low)), Math.max(Object.values(data.high))], 
            type: 'linear'
        },

        modebar: {
            bgcolor: 'transparent',
            color: 'white', 
            activecolor: 'gray',
        }
    };

    var options = {
        // scrollZoom: true,
        displaylogo: false, 
        modeBarButtonsToRemove: ['select2d', 'lasso2d'], 
        resposive: true,
    }

    Plotly.newPlot('upper-section', datawrap, layout, options);

    // SMA
    var trace2 = {
        x: Object.values(data.date),
        y: Object.values(data.sma),
        type: 'scatter'
    };
      
    var sma_data = [trace2];

    var layout2 = {
        plot_bgcolor:"transparent",
        paper_bgcolor:"transparent",
        dragmode: 'zoom', 
        margin: {
            r: 10, 
            t: 20, 
            b: 40, 
            l: 35
        }, 
        showlegend: false, 
        
        xaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            range: [data.date[0], data.date[999]], 
            rangeslider: {visible: false}, 
            // title: 'Date', 
            type: 'date'
        }, 
        yaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            range: [Math.min(Object.values(data.sma)), Math.max(Object.values(data.sma))], 
            type: 'linear'
        },

        modebar: {
            bgcolor: 'transparent',
            color: 'white', 
            activecolor: 'gray',
        }
    };
      
    Plotly.newPlot('nav-home', sma_data, layout2, options);

    // MACD
    var macd_data = {
        x: Object.values(data.date),
        y: Object.values(data.macd),
        type: 'scatter',
        name: 'macd'
      };

    var signal_data = {
        x: Object.values(data.date),
        y: Object.values(data.signal),
        type: 'scatter',
        name: 'signal'
    };

    var markerTag = [];
    Object.values(data.histogram).forEach(function(value){
        if(value < 0){
            markerTag.push('red');
        }else{
            markerTag.push('green');
        }
    });

    var hist_data = {
        x: Object.values(data.date),
        y: Object.values(data.histogram),
        type: 'bar',
        name: 'histogram',
        marker: {color: markerTag},
    }
      
    var macdwrap = [macd_data, signal_data, hist_data];

    var layout3 = {
        plot_bgcolor:"transparent",
        paper_bgcolor:"transparent",
        dragmode: 'zoom', 
        margin: {
            r: 10, 
            t: 20, 
            b: 40, 
            l: 35
        }, 
        showlegend: true, 

        legend: {
            font: {color: 'white'},
            x: 0,
            y: 10,
            "orientation": "h"
        },
        
        xaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            range: [data.date[0], data.date[999]], 
            rangeslider: {visible: false}, 
            // title: 'Date', 
            type: 'date'
        }, 
        yaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            // range: [Math.min(Object.values(data.low)), Math.max(Object.values(data.high))], 
            type: 'linear'
        },

        modebar: {
            bgcolor: 'transparent',
            color: 'white', 
            activecolor: 'gray',
        }
    };
      
    Plotly.newPlot('nav-profile', macdwrap, layout3, options);
    
    // RSI
    var trace_rsi = {
        x: Object.values(data.date),
        y: Object.values(data.rsi),
        type: 'scatter'
    };
      
    var rsi_data = [trace_rsi];

    var layout_rsi = {
        plot_bgcolor:"transparent",
        paper_bgcolor:"transparent",
        dragmode: 'zoom', 
        margin: {
            r: 10, 
            t: 20, 
            b: 40, 
            l: 35
        }, 
        showlegend: false, 
        
        xaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            range: [data.date[0], data.date[999]], 
            rangeslider: {visible: false}, 
            // title: 'Date', 
            type: 'date'
        }, 
        yaxis: {
            color: '#198754',
            gridcolor: 'rgba(255, 255, 255, 0.3)',
            autorange: true, 
            domain: [0, 1], 
            range: [Math.min(Object.values(data.rsi)), Math.max(Object.values(data.rsi))], 
            type: 'linear'
        },

        shapes: [
            {
              type: 'line',
              x0: data.date[0],
              y0: 30,
              x1: data.date[999],
              y1: 30,
              line: {
                color: 'red',
                width: 1,
              }
            },
            {
                type: 'line',
                x0: data.date[0],
                y0: 70,
                x1: data.date[999],
                y1: 70,
                line: {
                  color: 'yellow',
                  width: 1,
                }
              },
        ],

        modebar: {
            bgcolor: 'transparent',
            color: 'white', 
            activecolor: 'gray',
        }
    };
      
    Plotly.newPlot('nav-contact', rsi_data, layout_rsi, options);

});
}

function trade() {
    var term_val = document.getElementById('btn-dropdown-period').value;
    var symbol_val = document.getElementById('btn-dropdown-pair').value;
    var init_cash_val = document.getElementById('btn-input-money').valueAsNumber;

    console.log(init_cash_val);

    if(Number.isInteger(init_cash_val) === false){
        console.log('init value is not an integer');
        $('#bot-result').html(
            '<div class="alert alert-danger mt-3" role="alert">\
                本金必須為整數！\
            </div>');
        return;
    }

    console.log(term_val, symbol_val, init_cash_val);
    $('#btn-test').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 處理中');
    document.getElementById("btn-test").setAttribute("disabled", ""); 

    $('#bot-result').html(
        '<div class="d-flex justify-content-center align-items-center" style="height: 70vh;">\
            <div class="spinner-grow spinner-grow-sm text-light m-2" role="status">\
                <span class="visually-hidden">Loading...</span>\
            </div>\
            <div class="spinner-grow spinner-grow-sm text-light m-2" role="status">\
                <span class="visually-hidden">Loading...</span>\
            </div>\
            <div class="spinner-grow spinner-grow-sm text-light m-2" role="status">\
                <span class="visually-hidden">Loading...</span>\
            </div>\
        </div>'
    );
    

    $.getJSON(`http://localhost:8080/trade?term=${term_val}&symbol=${symbol_val}&init_cash=${init_cash_val}`, function(data){
        // var endPrice = data[0].toFixed(4);
        // document.getElementById('result').firstChild.data = endPrice.toString();
        console.log(data);

        var values = [
            ['Nearest', 'Best', 'Worst'],
            Object.values(data[0].end_value),
            Object.values(data[0].rsi)]
      
        var data = [{
        type: 'table',
        header: {
            values: [["<b>Period</b>"], ["<b>Ours</b>"], ["<b>RSI</b>"]],
            align: "center",
            line: {width: 1, color: '#198754'},
            fill: {color: "rgba(255, 255, 255, 0.7)"},
            font: {family: "Arial", size: 12, color: "#198754"}
        },
        cells: {
            values: values,
            align: "center",
            line: {color: "#198754", width: 1},
            font: {family: "Arial", size: 11, color: ["#198754"]}
        }
        }]
        
        var layout = {
            title: "Result Comparison",
            font: {color: 'white'},
            plot_bgcolor:"transparent",
            paper_bgcolor:"transparent",
            margin: {
                r: 25, 
                t: 110, 
                b: 0, 
                l: 20
            },
            modebar: {
                bgcolor: 'transparent',
                color: 'white', 
                activecolor: 'gray',
            }
        }

        $('#bot-result').html('');
        Plotly.newPlot('bot-result', data, layout, {displaylogo: false});
        
        $('#btn-test').html('回測');
        document.getElementById("btn-test").removeAttribute("disabled");
    });
}
