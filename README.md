# Prometheus Solax Exporter 

Prometheus exporter for the real time API metrics of Solax PV converters

## What does it do?

This repository contains a Python script that accesses the real-time API of a Solax branded solar panel converter, retrieves the metrics and exposes them into a format usable by Prometheus.

The "official" way to get metrics from a Solax exporter is to connect the device to your WiFi network and let it send data to the Solax servers in China, which you can then view through the Solax mobile app.

With this exporter, you can retrieve the data, store it in Prometheus and view it without your data having to leave your house.

## How to use it?

First, you need to have a Solax converter equipped with Solax' WiFi module.

This WiFi module broadcasts a network with the SSID being the serial number of the WiFi module. The network does not have any authentication.

Connect the device running the exporter (a Raspberry Pi works fine) to this network and run the script.

Then, simply configure your Prometheus instance to access the web interface exposed for this script to retrieve the metrics.

## Configuration

The script accepts the following environment variables:

- SOLAX_API_HOST: The address where the Solax web can be accessed. You should be able to find the address by inspecting the network information of the WiFi network, or by checking the manual of your converter for the address where to configure the WiFi connection (the metrics API is on the same interface).
- EXPORTER_PORT: The port where the metrics interface will be available on.

## Credits

Thanks to squishykid for developing the [Solax API client](https://github.com/squishykid/solax).

