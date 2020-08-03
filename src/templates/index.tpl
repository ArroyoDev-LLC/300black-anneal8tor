<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no"
    />

    <!-- Bootstrap CSS -->
    <link
      rel="stylesheet"
      href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
      integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk"
      crossorigin="anonymous"
    />

    <title>300Black Anneal8tor</title>
  </head>
  <body>
    {% include '_base.tpl' %}
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script
      src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
      integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
      crossorigin="anonymous"
    ></script>
    <script
      src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"
      integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo"
      crossorigin="anonymous"
    ></script>
    <script
      src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"
      integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI"
      crossorigin="anonymous"
    ></script>

    <script>
      var source = new EventSource("events");
      source.onmessage = function (event) {
        var alert = document.getElementById("alert-error");
        if (!alert.classList.contains("d-none")) {
          alert.classList.add("d-none");
        }
        var data = event.data.split(":");
        if (data[0].startsWith("pos")) {
          document.getElementById("position").innerHTML = data[1];
        }
        if (data[0].startsWith("state")) {
          document.getElementById("state").innerHTML = data[1];
        }
        if (data[0].startsWith("count")) {
          document.getElementById("count").innerHTML = data[1];
        }
        if (data[0].startsWith("error")) {
          $(`<div class="alert alert-danger alert-dismissible fade show" role="alert">
              <strong>Error!</strong> ${data[1]}.
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>`).prependTo($("#alerts"));
        }
      };

      source.onerror = function (event) {
        var alert = document.getElementById("alert-error");
        alert.innerHTML = "Event Source error: " + error;
        alert.classList.remove("d-none");
      };

      function setPos() {
        var pos = document.getElementById("posInput").value;
        console.log("setting position to:", pos);
        fetch("/set_pos?pos=" + pos);
      }

      function calibrate() {
        fetch("/calibrate");
      }

      function makeStep(step) {
        fetch("/move_slot?step=" + step);
      }

      // Handle Wireless config form
      $("#cfg-wifi-submit").click(function () {
        var ssid = $("#cfg-wifi-ssid").val();
        var pass = $("#cfg-wifi-pass").val();
        console.log("updating wireless config: " + ssid);
        fetch("/update_config?ssid=" + ssid + "&pass=" + pass);
      });

      // Handle power button.
      $("#pwr-toggle").click(function () {
        var pwr = $("#pwr-toggle");
        if (pwr.hasClass("btn-outline-danger")) {
          console.log("POWER: off => on");
          pwr.removeClass("btn-outline-danger");
          pwr.addClass("btn-outline-success");
          fetch("/update_config?power=1");
        } else {
          console.log("POWER: on => off");
          pwr.removeClass("btn-outline-success");
          pwr.addClass("btn-outline-danger");
          fetch("/update_config?power=0");
        }
      });
    </script>
  </body>
</html>
