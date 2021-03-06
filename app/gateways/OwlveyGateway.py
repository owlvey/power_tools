import datetime

import requests

from app.components.ConfigurationComponent import ConfigurationComponent


class OwlveyGateway:

    def __init__(self, configuration_component: ConfigurationComponent):
        self.host = configuration_component.owlvey_url
        self.identity = configuration_component.owlvey_identity
        self.token = None
        self.token_on = None
        self.client_id = configuration_component.owlvey_client
        self.client_secret = configuration_component.owlvey_secret

    @staticmethod
    def __validate_status_code(response):
        if response.status_code > 299:
            raise ValueError(response.text)

    def generate_token(self):
        payload = {
            "grant_type": "client_credentials",
            "scope": "api",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(self.identity + "/connect/token",
                                 data=payload)
        OwlveyGateway.__validate_status_code(response)
        self.token_on = datetime.datetime.now()
        self.token = response.json()

    def __build_authorization_header(self):
        if self.token:
            expires_in = self.token["expires_in"]
            if (self.token_on + datetime.timedelta(seconds=expires_in + 30)) > datetime.datetime.now():
                self.generate_token()
        else:
            self.generate_token()

        return {
            "Authorization": "Bearer " + self.token["access_token"]
        }

    def __internal_get(self, url):
        response = requests.get(url,
                                headers=self.__build_authorization_header(),
                                verify=False)
        OwlveyGateway.__validate_status_code(response)
        return response.json()

    def __internal_put(self, url, payload):
        response = requests.put(url, json=payload,
                                headers=self.__build_authorization_header(),
                                verify=False)
        OwlveyGateway.__validate_status_code(response)

    def __internal_delete(self, url, payload):
        response = requests.delete(url, json=payload,
                                   headers=self.__build_authorization_header(),
                                   verify=False)
        OwlveyGateway.__validate_status_code(response)

    def __internal_post(self, url, payload):
        response = requests.post(url, json=payload,
                                 headers=self.__build_authorization_header(),
                                 verify=False)
        OwlveyGateway.__validate_status_code(response)
        return response.json()

    def get_customers(self):
        return self.__internal_get(self.host + "/customers")

    def get_customer(self, name):
        customers = self.get_customers()
        for cus in customers:
            if cus['name'] == name:
                return cus
        return None

    def get_products(self, organization_id):
        return self.__internal_get(self.host + '/products?customerId={}'.format(organization_id))

    def get_product(self, organization_id, name):
        products = self.get_products(organization_id)
        for product in products:
            if product['name'] == name:
                return product
        return None

    def get_syncs(self, product_id):
        return self.__internal_get(self.host + "/products/{}/sync".format(product_id))

    def post_sync(self, product_id, name):
        return self.__internal_post(self.host + "/products/{}/sync/{}".format(product_id, name), {})

    def put_last_anchor(self, product_id, name, target):
        self.__internal_put(self.host + "/products/{}/sync/{}".format(product_id, name),
                            {"target": target.isoformat()})

    def get_features(self, product_id):
        return self.__internal_get(self.host + "/features?productId={}".format(product_id))

    def get_feature_detail(self, feature_id):
        return self.__internal_get(self.host + "/features/{}".format(feature_id))

    def create_customer(self, name):
        return self.__internal_post(self.host + "/customers", {"name": name})

    def create_product(self, customer_id, name):
        return self.__internal_post(self.host + "/products", {"customerId": customer_id, "name": name})

    def create_service(self, product_id, name, slo):
        service = self.__internal_post(self.host + "/services", {"productId": product_id, "name": name})
        service_id = service["id"]
        service["slo"] = slo
        self.__internal_put(self.host + "/services/" + str(service_id), service)
        return service

    def assign_indicator(self, feature_id, source_id):
        return self.__internal_put(self.host + "/features/{}/indicators/{}".format(feature_id, source_id), {})

    def un_assign_indicator(self, feature_id, source_id):
        return self.__internal_delete(self.host + "/features/{}/indicators/{}".format(feature_id, source_id), {})

    def create_feature(self, product_id, name):
        return self.__internal_post(self.host + "/features", {"productId": product_id, "name": name})

    def create_incident(self, product_id, key, title, resolution_on: datetime, ttd, tte, ttf, url):
        response = requests.post(self.host + "/incidents", json={"productId": product_id,
                                                                 "key": key,
                                                                 "title": title
                                                                 },
                                 verify=False)
        OwlveyGateway.__validate_status_code(response)
        incident_id = response.json()["id"]
        response = requests.put(self.host + "/incidents/{}".format(incident_id),
                                json={"title": title, "ttd": ttd, "tte": tte, "ttf": ttf, "url": url,
                                      "affected": 1,
                                      "end": resolution_on.isoformat()},
                                verify=False)
        OwlveyGateway.__validate_status_code(response)

        return response.json()

    def assign_incident_feature(self, incident_id, feature_id):
        response = requests.put(self.host + "/incidents/{}/features/{}".format(incident_id, feature_id),
                                verify=False)
        OwlveyGateway.__validate_status_code(response)

    def get_sources(self, product_id):
        return self.__internal_get(self.host + "/sources?productId={}".format(product_id))

    def create_source(self, product_id, name, kind, group,
                      good_definition: str = "", total_definition: str = ""):
        result = self.__internal_post(self.host + "/sources",
                                    {
                                        "productId": product_id,
                                        "name": name,
                                        "kind": kind,
                                        "group": group
                                    })

        result["goodDefinition"] = good_definition
        result["totalDefinition"] = total_definition

        self.__internal_put(self.host + "/sources/{}".format(result["id"]), result)

        return result

    def create_sli(self, feature_id, source_id):
        self.__internal_put(self.host + "/features/{}/indicators/{}".format(feature_id, source_id), {})

    def search_feature(self, product_id, name):
        return self.__internal_get(self.host + "/features/search?productId={}&name={}".format(product_id, name))

    def create_source_item(self, source_id, start, total, good):

        return self.__internal_post(self.host + "/sourceItems",
                                    {
                                        "sourceId": source_id,
                                        "start": start.isoformat(),
                                        "end": start.isoformat(),
                                        "total": int(total),
                                            "good": int(good)
                                     })

    def create_source_item_proportion(self, source_id, start, percent):

        result = self.__internal_post(self.host + "/sourceItems/proportion",
                                      {
                                        "sourceId": source_id,
                                        "start": start.isoformat(),
                                        "end": start.isoformat(),
                                        "proportion": percent,
                                      })

        return result













