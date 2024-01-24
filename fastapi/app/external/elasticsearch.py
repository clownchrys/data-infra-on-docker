from elasticsearch import Elasticsearch

HOSTNAME = "elasticsearch"
PORT = 9200
SCHEME = "http"

client = Elasticsearch(
    hosts=f"{SCHEME}://{HOSTNAME}:{PORT}",
    connections_per_node=2,
    max_retries=5,
    request_timeout=30, # same as timeout
    randomize_nodes_in_pool=True, # same as randomize_hosts

    sniff_on_start=True,
    sniff_before_requests=False,
    sniff_timeout=30,

    # sniffer_timeout=30, # ValueError: Can't specify both 'sniffer_timeout' and 'min_delay_between_sniffing', instead only specify 'min_delay_between_sniffing'
    min_delay_between_sniffing=60,

    # sniff_on_connection_fail=True, # ValueError: Can't specify both 'sniff_on_connection_fail' and 'sniff_on_node_failure', instead only specify 'sniff_on_node_failure'
    sniff_on_node_failure=True,
)