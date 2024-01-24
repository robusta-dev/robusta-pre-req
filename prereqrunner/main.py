import logging
import os
from typing import Optional
from kubernetes import config
from prereqrunner.api_server import ApiServer
from prereqrunner.discovery import Discovery, DiscoveryResults


def run_checks():
    # run discovery checks
    discovery_output: Optional[DiscoveryResults] = None
    for _ in range(0,2):
        try:
            discovery_output = Discovery.discovery_process()
            Discovery.discover_stats()
        except Exception:
            logging.exception("Discovery check failed")

    if discovery_output:
        ApiServer.run_checks(discovery_output)
    else:
        logging.info("Skipped api server checks, no discovery output")

def load_cluster_config():
    try:
        if os.getenv("KUBERNETES_SERVICE_HOST"):
            config.load_incluster_config()
        else:
            config.load_kube_config()
    except config.config_exception.ConfigException as e:
        logging.warning(f"Running without kube-config! e={e}")


if __name__ == '__main__':
    logging.getLogger().setLevel("INFO")
    load_cluster_config()
    logging.info("Stating Robusta pre-requisites tests..")
    run_checks()
    logging.info("Finished Robusta pre-requisites tests")

