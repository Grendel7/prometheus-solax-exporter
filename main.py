import os
import solax
from prometheus_client import Gauge, CollectorRegistry, Info
from prometheus_client.exposition import generate_latest
from aiohttp import web
from solax.inverter import DiscoveryError
import asyncio

import logging


class SolaxWebApplication(object):
    def __init__(self, api_host):
        self.api_host = api_host
        self.real_time_api = None
        self.sensor_map = None

    async def connect_to_solax(self, *args):
        try:
            self.real_time_api = await asyncio.wait_for(solax.real_time_api(self.api_host), 5)
        except DiscoveryError as e:
            logging.error(e)
            return False
        except asyncio.TimeoutError as e:
            logging.error(f"Timeout while connection to {self.api_host}")
            return False
        else:
            self.sensor_map = self.real_time_api.inverter.sensor_map()

        return True

    async def index(self, request):
        return web.Response(text="Prometheus metrics available on /metrics")

    async def metrics(self, request):
        registry = await self.get_metrics_registry()

        return web.Response(body=generate_latest(registry), content_type='text/plain')

    async def get_metrics_registry(self):
        registry = CollectorRegistry(auto_describe=True)

        # Error case 1: The exporter has never connected to the inverter.
        if not self.real_time_api:
            connect_result = await self.connect_to_solax()

            if not connect_result:
                self.set_up_metric(False, registry)
                return registry

        # Error case 2: The exporter has lost it's connection to the inverter.
        try:
            response = await self.real_time_api.get_data()
        except solax.inverter.InverterError as e:
            logging.error(e)
            self.set_up_metric(False, registry)
            return registry

        info_metric = Info('solax_inverter_info', 'Information about the Solax inverter', registry=registry)
        info_metric.info({
            'serial_number': response.serial_number,
            'type': response.type,
            'version': response.version,
        })

        for metric_name, metric_value in response.data.items():
            _, metric_unit = self.sensor_map[metric_name]

            metric_class = Gauge

            safe_metric_name = "solax_" + metric_name.lower().replace("\'", "").replace(' ', '_').replace('-', '_')
            metric_obj = metric_class(safe_metric_name, f"{metric_name} in {metric_unit}", registry=registry)
            metric_obj.set(metric_value)

        return registry

    def set_up_metric(self, success, registry):
        up_metric = Gauge('solax_up', 'Whether the Solax inverter is reachable', registry=registry)
        up_metric.set(int(success))


solax_app = SolaxWebApplication(os.environ.get('SOLAX_API_HOST'))

app = web.Application()
app.on_startup.append(solax_app.connect_to_solax)
app.router.add_get('/', solax_app.index)
app.router.add_get('/metrics', solax_app.metrics)
web.run_app(app, port=os.environ.get('EXPORTER_PORT', 8080))
