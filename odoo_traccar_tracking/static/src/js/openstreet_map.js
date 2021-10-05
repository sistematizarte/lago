/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('odoo_traccar_tracking.openstreet_map_js', function (require) {
    "use strict";

    var FormRenderer = require("web.FormRenderer");
    var ajax = require('web.ajax');

    var UrlOsrmRoute = '//router.project-osrm.org/route/v1/driving/';

    var styles = {
      route: new ol.style.Style({
        stroke: new ol.style.Stroke({
          width: 6, color: [8, 114, 29, 1]
        })
      }),
      icon: new ol.style.Style({
        image: new ol.style.Icon({
          anchor: [0.5, 1],
          src: 'http://cdn.rawgit.com/openlayers/ol3/master/examples/data/icon.png'
        })
      }),
      cluster: function (size) {
        return new ol.style.Style({
          image: new ol.style.Circle({
            radius: 10,
            stroke: new ol.style.Stroke({
              color: '#fff',
            }),
            fill: new ol.style.Fill({
              color: [8, 114, 29, 1],
            }),
          }),
          text: new ol.style.Text({
            text: size.toString(),
            fill: new ol.style.Fill({
              color: '#fff',
            }),
          }),
        })
      }
    }


    FormRenderer.include({

      _renderView: function () {
        var self = this;
        var res = this._super.apply(this, arguments);
        return res.then(function () {
          self._map = self.$el.find('#traccarMap');
          self._map.append('<div id="popup" />');
          self.element_popup = self._map.find('#popup');
          if (self._map.length > 0) {
            self.render_openstreet_map();
          }
        })
      },

      render_openstreet_map: function() {
        var self = this;
        this.vectorSource = new ol.source.Vector();
        this.vectorLayer = new ol.layer.Vector({
          source: this.vectorSource
        });
        this.map = new ol.Map({
          target: this._map[0],
          layers: [
            new ol.layer.Tile({
              source: new ol.source.OSM()
            }),
          ],
          view: new ol.View({
            center: ol.proj.fromLonLat([0, 0]),
            zoom: 1
          })
        });

        this.vectorSource.clear();

        this.popup = new ol.Overlay({
          element: this.element_popup[0],
          positioning: 'bottom-center',
          stopEvent: false,
          offset: [0, -20],
        });
        this.map.addOverlay(this.popup);

        //create route b/w two point given in model form veiw
        if (this._map.attr('route') == 'true') {
          this.createRouteForPoints();
          this.map.on('click', function (evt) {
            var feature = self.map.forEachFeatureAtPixel(evt.pixel, function (feature) {
              return feature;
            });
            if (feature) {
              self.element_popup.popover('dispose');
              var coordinates = feature.getGeometry().getCoordinates();
              self.popup.setPosition(coordinates);
              self.element_popup.popover({
                placement: 'top',
                html: true,
                content: feature.get('name'),
              });
              self.element_popup.popover('show');
            } else {
              self.element_popup.popover('dispose');
            }
          })
        }
        // marker for all active driver
        if (this._map.attr('feature') == 'true') {
          this.activeDriverLocations();
          this.map.on('click', function (evt) {
            var feature = self.map.forEachFeatureAtPixel(evt.pixel, function (feature) {
              return feature;
            });
            if (feature) {
              feature = feature.get('features');
              if (feature.length == 1) {
                feature = feature[0];
                self.element_popup.popover('dispose');
                var coordinates = feature.getGeometry().getCoordinates();
                self.popup.setPosition(coordinates);
                self.element_popup.popover({
                  placement: 'top',
                  html: true,
                  content: feature.get('name'),
                });
                self.element_popup.popover('show');
              } else {
                self.element_popup.popover('dispose');
              }
            } else {
              self.element_popup.popover('dispose');
            }
          });
        }

        self.map.on('pointermove', function (e) {
          if (e.dragging) {
            self.element_popup.popover('dispose');
            return;
          }
          var pixel = self.map.getEventPixel(e.originalEvent);
          var hit = self.map.hasFeatureAtPixel(pixel);
          self.map.getTarget().style.cursor = hit ? 'pointer' : '';
        });

        $(document).on('click', function (el) {
          if (el.target.tagName != 'CANVAS') {
            self.element_popup.popover('dispose');
          }
        })

        $(document).on('mouseover', function (el) {
          self.map.updateSize();
        })
      },


      activeDriverLocations: function () {
        var self = this;
        var locations = self.state.data.driver_locations;
        if (locations) {
          self.markers = [];
          locations = locations.split(';');
          for (var i = 0; i < locations.length; i++) {
            var marker = self.createFeature(self.parseResponse(locations[i]));
            self.markers.push(marker);
          }
          self.MarkerClusterer();
        }
      },

      createRouteForPoints: function () {
        var self = this;
        var detail = this.state.data;
        var point_1 = {
          long: detail.source_lat,
          lat: detail.source_long,
          name: detail.source_lat + ',' + detail.source_long
        };

        var point_2 = {
          long: detail.destination_lat,
          lat: detail.destination_long,
          name: detail.destination_lat + ',' + detail.destination_long
        };

        // var point_2 = [detail.destination_lat, detail.destination_long];
        var url = `${UrlOsrmRoute}${point_1.name};${point_2.name}`;


        fetch(url).then(function (response) {
          return response.json();
        }).then(function (json) {
          self.vectorSource.addFeature(self.createFeature(point_1));
          self.vectorSource.addFeature(self.createFeature(point_2));
          if (json.code.toUpperCase() == 'OK') {
            var polyline = json.routes[0].geometry;
            var route = (new ol.format.Polyline({
              factor: 1e5
            }).readGeometry(polyline, {
              dataProjection: 'EPSG:4326',
              featureProjection: 'EPSG:3857'
            }));
            var feature = new ol.Feature({
              type: 'route',
              geometry: route
            });
            feature.setStyle(styles.route);
            self.vectorSource.addFeature(feature);
            self.map.addLayer(self.vectorLayer);
          }
        });
      },

      createFeature: function(coord) {
        var content = `<p class='font-weight-bold mb-0'>${coord.name}</p>`;
        var feature = new ol.Feature({
          geometry: new ol.geom.Point(ol.proj.fromLonLat([coord.long, coord.lat])),
          name: content
        });
        feature.setStyle(styles.icon)
        return feature
      },

      parseResponse: function (data) {
        var location = data.split(":");
        var response = {name: location[0]};
        location = location[1].split(',');
        response.lat = location[0];
        response.long = location[1];
        return response;
      },

      MarkerClusterer: function () {
        var self = this;
        var styleCache = {};
        this.vectorSource = new ol.source.Vector({
         features: self.markers,
        });

       var clusterSource = new ol.source.Cluster({
          distance: parseInt(10),
          source: this.vectorSource,
        });

        this.vectorLayer = new ol.layer.Vector({
          source: clusterSource,
          style: function (feature) {
            var size = feature.get('features').length;
            var style = styleCache[size];
            if (!style) {
              var style = false;
              if (size == 1) {
                style = styles.icon;
              }
              else {
                style = styles.cluster(size);
              }
              styleCache[size] = style;
            }
            return style;
          }
        })
        this.map.addLayer(this.vectorLayer);
      }
    });
  })
