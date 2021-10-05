/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('odoo_traccar_tracking.google_map_js', function (require) {
    "use strict";
    var FormRenderer = require("web.FormRenderer");
    var ajax = require('web.ajax');

    var options = {
        imagePath: '/odoo_traccar_tracking/static/src/lib/m'
    };


    FormRenderer.include({
      _renderView: function () {
        var self = this;
        var res = this._super.apply(this, arguments);
        return res.then(function () {
          self._map = self.$el.find('#traccarMap');
          if (self._map.length > 0) {
            self.render_google_map();
          }
        })
      },

      render_google_map: function () {
        this.map = new google.maps.Map(this._map[0], {
            zoom: 2,
            center: {
                lat: 41.85,
                lng: -87.65
            }
        });

        //create route b/w two point given in model form veiw
        if (this._map.attr('route') == 'true') {
          this.createRouteForPoints();
        }
        // marker for all active driver
        if (this._map.attr('feature') == 'true') {
          this.activeDriverLocations();
        }
      },

      createRouteForPoints: function () {
        var directionsService = new google.maps.DirectionsService();
        var directionsRenderer = new google.maps.DirectionsRenderer();
        var detail = this.state.data;
        var self = this;
        directionsRenderer.setMap(this.map);

        if (detail.source_long) {
            var start = detail.source_long + ',' + detail.source_lat;
            var end = detail.destination_long + ',' + detail.destination_lat;
            calculateAndDisplayRoute(directionsService, directionsRenderer);
            function calculateAndDisplayRoute(directionsService, directionsRenderer) {
                directionsService.route({
                    origin: start,
                    destination: end,
                    travelMode: google.maps.TravelMode.DRIVING
                },(response, status) => {
                    if (status === "OK") {
                        directionsRenderer.setDirections(response);
                    } else {
                        self._map.append(`
                          <p class='alert alert-danger'>
                            Goggle map direction api is not responding.Please see in
                            <a target="new" href="//developers.google.com/maps/documentation/directions/usage-and-billing">
                             usage-and-billing Google directions Api.
                            </a>
                          </p>
                      `);
                    }
                });
            }
        }
      },

      activeDriverLocations: function () {
        var self = this;
        var locations = self.state.data.driver_locations;
        if (locations) {
          self.infoWindow = new google.maps.InfoWindow();
          self.markers = [];
          locations = locations.split(';');

          for (var i = 0; i < locations.length; i++) {
            self.createFeature(self.parseResponse(locations[i]));
          }

          google.maps.event.addListener(self.map, 'click', function() {
            self.infoWindow.close();
          });

          new MarkerClusterer(self.map, self.markers, options);
        }
      },

      parseResponse: function (data) {
        var location = data.split(":");
        var response = {name: location[0]};
        location = location[1].split(',');
        response.lat = location[0];
        response.long = location[1];
        return response;
      },

      createFeature: function (coord) {
        console.log(coord);
        var self = this;
        var latLng = new google.maps.LatLng(coord.lat, coord.long);
        // var
        var marker = new google.maps.Marker({
            partner: coord.name,
            map: this.map,
            position: latLng
        });

        var onMarkerClick = function() {
          var content = `<p class="font-weight-bold mb-0">${this.partner}</p>`
          self.infoWindow.setContent(content);
          self.infoWindow.open(self.map, this);
        };

        google.maps.event.addListener(marker, 'click', onMarkerClick);
        self.markers.push(marker);
      },


    });

  })
