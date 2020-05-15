from app.components.ConfigurationComponent import ConfigurationComponent
from app.gateways.OwlveyGateway import OwlveyGateway


class RegistrationComponent:

    def __init__(self, configuration: ConfigurationComponent = None,
                 owlvey: OwlveyGateway = None):

        self.configuration = configuration or ConfigurationComponent()
        self.owlvey = owlvey or OwlveyGateway(self.configuration)

    def auto_un_register_latency_experienc(self, organization, product):
        organization_ins = self.owlvey.get_customer(organization)
        product_ins = self.owlvey.get_product(organization_ins['id'], product)

        features = self.owlvey.get_features(product_ins['id'])

        features_details = list()

        for feature in features:
            features_details.append(self.owlvey.get_feature_detail(feature['id']))

        sources = self.owlvey.get_sources(product_ins['id'])
        availability_sources = list()
        latency_sources = list()
        experience_sources = list()

        for source in sources:
            if source['group'] == 'Availability':
                availability_sources.append(source)
            if source['group'] == 'Latency':
                latency_sources.append(source)
            if source['group'] == 'Experience':
                experience_sources.append(source)

        for feature in features_details:
            slis = feature['indicators']
            for sli in slis:
                sli_source = next((x for x in availability_sources if x['id'] == sli['sourceId']), None)
                if sli_source:
                    sli_latency = next((x for x in latency_sources if sli_source['name'] in x['name']), None)
                    if sli_latency:
                        self.owlvey.un_assign_indicator(feature['id'], sli_latency['id'])

                    sli_experience = next((x for x in experience_sources if sli_source['name'] in x['name']), None)
                    if sli_experience:
                        self.owlvey.un_assign_indicator(feature['id'], sli_experience['id'])


    def auto_register_latency_experience(self, organization, product):
        organization_ins = self.owlvey.get_customer(organization)
        product_ins = self.owlvey.get_product(organization_ins['id'], product)

        features = self.owlvey.get_features(product_ins['id'])

        features_details = list()

        for feature in features:
            features_details.append(self.owlvey.get_feature_detail(feature['id']))

        sources = self.owlvey.get_sources(product_ins['id'])
        availability_sources = list()
        latency_sources = list()
        experience_sources = list()

        for source in sources:
            if source['group'] == 'Availability':
                availability_sources.append(source)
            if source['group'] == 'Latency':
                latency_sources.append(source)
            if source['group'] == 'Experience':
                experience_sources.append(source)

        for feature in features_details:
            slis = feature['indicators']
            for sli in slis:
                sli_source = next((x for x in availability_sources if x['id'] == sli['sourceId']), None)
                if sli_source:
                    sli_latency = next((x for x in latency_sources if sli_source['name'] in x['name']), None)
                    if sli_latency:
                        self.owlvey.assign_indicator(feature['id'], sli_latency['id'])

                    sli_experience = next((x for x in experience_sources if sli_source['name'] in x['name']), None)
                    if sli_experience:
                        self.owlvey.assign_indicator(feature['id'], sli_experience['id'])











