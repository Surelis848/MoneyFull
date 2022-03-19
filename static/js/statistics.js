/*--------------------General--------------------*/


// 'Add Purchase' form resubmission on page reload

if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
}

// getting today's date as a default when page fully loads

window.onload = function() {
  $(document).ready(function() {
    try {
      get_current_Month();
    }
    catch (error) {
      console.error(error);
    }
    try {
      get_today();
    }
    catch (error) {
      console.error(error);
    }
});
}

function get_today() {
  document.getElementById("myDate").value = new Date().toISOString().substr(0, 10);
};

function get_current_Month() {
  const month = ["January","February","March","April","May","June","July","August","September","October","November","December"];

  const d = new Date();
  let currentMonth = month[d.getMonth()];
  document.getElementById("currentMonth").innerHTML = currentMonth;

 // document.getElementById("currentMonth").innerHTML = month[new Date().getMonth()];
};

queue()
    .defer(d3.json, "/moneyfull/Tracker")
    .await(makeCharts);

function makeCharts(error, moneyfullData) {
  var ndx = crossfilter(moneyfullData);
  var parseDate = d3.time.format("%Y-%m-%d").parse;

  moneyfullData.forEach(function(d) {
    d.spendDate = parseDate(d["date"]);
    d.amount = parseInt(d["amount"]);
    d.totalAmount = +d["amount"];

  });

  show_categories(ndx);
  show_amount(ndx);
  show_totals_amount(ndx);
  show_totals_days(ndx);
  show_categories_amount(ndx);

  dc.renderAll();

    // var overlay = document.getElementById("overlay");
    // overlay.style.display = "none";

};

/*--------------------Totals--------------------*/

function show_totals_amount(ndx) {
  var totalAmount = ndx.groupAll().reduceSum(function(d) {return d["totalAmount"];});

  dc.numberDisplay("#totalAmount")
      .formatNumber(d3.format("d"))
      .valueAccessor(function(d){return d;})
      .group(totalAmount)
      .formatNumber(d3.format(".3s"));
}

function show_totals_days(ndx) {
  var totalDays = ndx.groupAll();

  dc.numberDisplay("#totalEntries")
      .formatNumber(d3.format("d"))
      .valueAccessor(function(d){return d;})
      .group(totalDays)

}

/*--------------------Amount--------------------*/

function show_amount(ndx) {
    var dateDim = ndx.dimension(function(d) { return d["spendDate"]; });
    var minDate = dateDim.bottom(1)[0].spendDate;
    var maxDate = dateDim.top(1)[0].spendDate;

    var amountGroup = dateDim.group().reduceSum(dc.pluck("amount"))

    dc.lineChart("#amount_date_chart")
      .width(900)
      .height(500)
      .useViewBoxResizing(true)
      .margins({ top: 20, right: 40, bottom: 30, left: 80 })
      .dimension(dateDim)
      .group(amountGroup, "Amount")
      .transitionDuration(500)
      .x(d3.time.scale().domain([minDate, maxDate]))
      .elasticX(true)
      .yAxisLabel("Amount(€)")
      .controlsUseVisibility(true);

}

/*--------------------Categories--------------------*/

function show_categories_amount(ndx) {
    var categoryDim = ndx.dimension(dc.pluck("category"));
    var amountGroup = categoryDim.group().reduceSum(dc.pluck("amount"))

    dc.rowChart("#category_amount_chart")
        .width(768)
        .height(500)
        .useViewBoxResizing(true)
        .dimension(categoryDim)
        .group(amountGroup)
        .transitionDuration(500)
        .elasticX(true)
        .controlsUseVisibility(true);
}

function show_categories(ndx) {
    var categoryDim = ndx.dimension(dc.pluck("category"));
    var categoryGroup = categoryDim.group()

    dc.pieChart("#category_chart")
        .width(400)
        .height(150)
        .useViewBoxResizing(true)
        .dimension(categoryDim)
        .group(categoryGroup)
        .transitionDuration(500)
        .legend(dc.legend().x(20).y(20).itemHeight(15).gap(5));
}



