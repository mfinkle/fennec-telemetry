// Generated by CoffeeScript 1.6.3
(function() {
  var $ = jQuery;
  var makeChart = function() {
    return function(pivotData, opts) {
      var defaults = {
        localeStrings: {
          vs: "vs",
          by: "by"
        }
      };
      opts = $.extend(defaults, opts);

      var rowKeys = pivotData.getRowKeys();
      if (rowKeys.length === 0) {
        rowKeys.push([]);
      }

      var colKeys = pivotData.getColKeys();
      if (colKeys.length === 0) {
        throw "We need a column";
      }

      var dataMap = {};
      var dataMin = Number.MAX_VALUE;
      var dataMax = 0;

      var colKey = colKeys[0];
      for (var i = 0, len = rowKeys.length; i < len; i++) {
        var rowKey = rowKeys[i];
        var agg = pivotData.getAggregator(rowKey, colKey);
        if (agg.value() != null) {
          dataMap[rowKey.join(":")] = agg.value();
          if (dataMin > agg.value())
            dataMin = agg.value();
          if (dataMax < agg.value())
            dataMax = agg.value();
        } else {
          dataMap[rowKey.join(":")] = null;
        }
      }

      var result = $("<div>", { width: "100%", height: "100%" });
      var canvas = $("<canvas/>");
      canvas[0].width = 900;
      canvas[0].height = 780;
      result.append(canvas);
      var ctx = canvas[0].getContext("2d");
      var img = new Image();
      img.onload = function(){
        ctx.drawImage(img, 0, 0);

        $.ajax({ url: "uitelemetry-exploded.csv", dataType: "text" }).done(function(data) {
          var input = $.csv.toObjects(data);
          for (var i=0; i<input.length; i++) {
            var value = dataMap[input[i].method + ":" + input[i].action];
            if (value) {
              var intensity = Math.round(255 * (value - dataMin) / (dataMax - dataMin));
              ctx.fillStyle = "rgba(255, 0, 0, " + (intensity / 255.0) + ")";
              ctx.fillRect(input[i].x, input[i].y, input[i].width, input[i].height);
            }
          }
        });
      };
      img.src = "uitelemetry-exploded.png";
      return result;
    };
  };

  $.pivotUtilities.other_renderers = {
    "UI Heatmap": makeChart()
  };
}).call(this);
