import argparse
import docker
import time

from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server


def resource_reservation_usage(docker_client):
    containers = docker_client.containers.list()
    return (
        sum(container.attrs['HostConfig']['NanoCpus'] for container in containers),
        sum(container.attrs['HostConfig']['Memory'] for container in containers),
    )


def node_resources(docker_client):
    info = docker_client.info()
    return (
        info["NCPU"] * 1e9,
        info["MemTotal"],
    )


class CustomCollector(object):
    def __init__(self):
        self.docker_client = docker.from_env()

    def collect(self):
        total_cpu, total_memory = node_resources(self.docker_client)
        yield GaugeMetricFamily("docker_node_cpu_total", 'total cpu of the node', value=total_cpu)
        yield GaugeMetricFamily("docker_node_memory_total", 'total memory of the node', value=total_memory)

        used_cpu, used_memory = resource_reservation_usage(self.docker_client)
        yield GaugeMetricFamily("docker_node_reserved_cpu_total", 'cpu reserved on the node', value=used_cpu)
        yield GaugeMetricFamily("docker_node_reserved_memory_total", 'memory reserved on the node', value=used_memory)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--port",
        type=int,
        default=9492,
        help="port",
    )
    opts = arg_parser.parse_args()

    start_http_server(opts.port)
    REGISTRY.register(CustomCollector())

    while True:
        time.sleep(1)
