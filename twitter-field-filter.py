from procstream import StreamProcessMicroService
import os
import json
import logging as logger

config = {"MODULE_NAME": os.environ.get('MODULE_NAME', 'LEWS_USER_CLASSIFICATION'),
          "CONSUMER_GROUP": os.environ.get("CONSUMER_GROUP", "LEWS_USER_CLASSIFICATION_CG"),
          "FILTER_CONFIG_FILENAME": os.environ.get("CLASS_FILENAME", "filter_config.json")}


class StreamTweetFieldFilter(StreamProcessMicroService):

    def read_config_file(self):
        filter_config = {}
        logger.info(f"Loading configuration file {self.config.get('FILTER_CONFIG_FILENAME')}")
        with open(self.config.get("FILTER_CONFIG_FILENAME"), 'r')as f:
            self.filter_config = json.load(f)
            logger.info(f"filter_config:{self.filter_config}")

    def __init__(self, config_new):
        super().__init__(config_new)
        self.filter_config = {}
        self.read_config_file()

    def read_node(self, node_key, input_payload):
        if node_key.find(".") != -1:
            return self.read_node(node_key[node_key.find(".") + 1:],
                                  input_payload.get(node_key[:node_key.find(".")])) \
                if isinstance(input_payload, dict) and input_payload.get(node_key[:node_key.find(".")]) else ""
        else:
            return input_payload.get(node_key) if isinstance(input_payload, dict) and \
                                                  input_payload.get(node_key) else ""

    def process_message(self, message):
        incoming_payload = message.value
        output_payload = {}
        for field in self.filter_config.get("include"):
            output_payload[field] = self.read_node(field, incoming_payload)
        return output_payload


def main():
    k_service = StreamTweetFieldFilter(config)
    k_service.start_service()


if __name__ == "__main__":
    main()


# def read_node(node_key, input_payload):
#     if node_key.find(".") != -1:
#         return read_node(node_key[node_key.find(".") + 1:],
#                          input_payload.get(node_key[:node_key.find(".")])) \
#             if isinstance(input_payload, dict) and input_payload.get(node_key[:node_key.find(".")]) else ""
#     else:
#         return input_payload.get(node_key) if isinstance(input_payload, dict) and \
#                                               input_payload.get(node_key) else ""
#
#
# # test_dict = {
# #     "user": {
# #         "name": {
# #             "first": "Nipun"
# #         }
# #     }
# # }
# #
# # print(read_node("user.name.first1", test_dict))
