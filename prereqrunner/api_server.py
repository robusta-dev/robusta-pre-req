import logging
import time
from random import randint

from typing import List, Optional

from hikaru.model.rel_1_26 import Pod, LabelSelector, LabelSelectorRequirement, PodList, Deployment, Node
from kubernetes.client import V1NodeList, V1Node

from prereqrunner.discovery import DiscoveryResults
from prereqrunner.model.services import ServiceInfo


def _get_match_expression_filter(expression: LabelSelectorRequirement) -> str:
    if expression.operator.lower() == "exists":
        return expression.key
    elif expression.operator.lower() == "doesnotexist":
        return f"!{expression.key}"

    values = ",".join(expression.values)
    return f"{expression.key} {expression.operator} ({values})"


def build_selector_query(selector: LabelSelector) -> str:
    label_filters = [f"{label[0]}={label[1]}" for label in selector.matchLabels.items()]
    label_filters.extend([_get_match_expression_filter(expression) for expression in selector.matchExpressions])
    return ",".join(label_filters)


class ApiServer:

    @staticmethod
    def get_node_pods(node_name: str) -> List[Pod]:
        start_t = time.time()
        pods = PodList.listPodForAllNamespaces(field_selector=f"spec.nodeName={node_name}").obj.items
        logging.info(f"Get node pods for {node_name} took {time.time() - start_t}")
        return pods

    @classmethod
    def get_pods_by_selector(cls, namespace: str, selector: LabelSelector) -> List[Pod]:
        start_t = time.time()
        selector = build_selector_query(selector)
        pods = PodList.listNamespacedPod(namespace=namespace, label_selector=selector).obj.items
        logging.info(f"Get pods by selector for {namespace}/{selector} took {time.time() - start_t}")
        return pods

    @classmethod
    def get_random_service(cls, services: List[ServiceInfo], kind: str) -> Optional[ServiceInfo]:
        kind_services = [dep for dep in services if dep.service_type == kind]
        if not kind_services:
            return None
        return kind_services[randint(0, len(kind_services) - 1)]

    @classmethod
    def get_random_node(cls, nodes: V1NodeList) -> Optional[V1Node]:
        if not nodes or not nodes.items:
            return None
        return nodes.items[randint(0, len(nodes.items) - 1)]

    @classmethod
    def run_checks(cls, results: DiscoveryResults):
        logging.info("Starting API Server checks....")
        for _ in range(0,3):
            try:
                deployment = cls.get_random_service(results.services, "Deployment")
                if deployment:
                    start_t = time.time()
                    obj = Deployment.readNamespacedDeployment(name=deployment.name, namespace=deployment.namespace).obj
                    logging.info(f"Hikaru read deployment {deployment.namespace}/{deployment.name} took {time.time() - start_t}")
                    cls.get_pods_by_selector(deployment.namespace, obj.spec.selector)
                else:
                    logging.info("Skipping hikaru deployment checks")

                node = cls.get_random_node(results.nodes)
                if node:
                    start_t = time.time()
                    obj = Node.readNode(name=node.metadata.name).obj
                    logging.info(f"Hikaru read node {node.metadata.name} took {time.time() - start_t}")
                    cls.get_node_pods(node.metadata.name)
                else:
                    logging.info("Skipping hikaru node checks")

            except Exception:
                logging.exception("Failed to run api server checks")
        logging.info("Finished API Server checks....")
