#!/usr/bin/python

import re
import sys
import os
import time
import socket

sys.path.insert(0, os.path.join( os.path.dirname(__file__), '/splunklibs/lib/python2.7/site-packages'))
from splunklib.client import connect as splunk_connect
import splunklib.results as splunk_results_parser
from prometheus_client.core import REGISTRY, CounterMetricFamily, GaugeMetricFamily
from prometheus_client import start_http_server

splunk_config_file = '/opt/splunkforwarder/etc/apps/SplunkUniversalForwarder/local/inputs.conf'
splunk_query_config_file = '/tmp/defaults/metrics_collection.conf'
loop_sleep_time_seconds = 60
expected_net_dev_name = 'eth0'
metrics_output_file = '/var/lib/prometheus/textfile/splunk_forwarder.prom'
prometheus_exporter_port = 9001

# Collect stats from the network device
class NetDevCollector(object):
    def __init__(self, expected_net_dev_name):
        self.find_net_dev_name = re.compile(r'\s*' + expected_net_dev_name + r':')
        self.extract_stats = re.compile(r':\s+(?P<rx_bytes>\d+)\s+(?P<rx_packets>\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(?P<tx_bytes>\d+)\s+(?P<tx_packets>\d+)')

    def collect(self):
        with open('/proc/net/dev') as fh:
            for line in fh:
                if self.find_net_dev_name.match(line):
                    match = self.extract_stats.search(line)
                    if match:
                        net_counter = CounterMetricFamily('splunk_forwarder_network', 'Splunk container network counters for %s' % (expected_net_dev_name), labels=['name'])
                        for k in ['rx_bytes', 'rx_packets','tx_bytes','tx_packets']:
                            net_counter.add_metric([ k ], match.group(k))
                        yield net_counter


# Collect stats from the central IT instance of splunk about this particular host
class SplunkStatsCollector(object):
    def __init__(self, splunk_config_file, splunk_server, username, password):
        #self.hostname = self.resolve_host_from_splunk_config(splunk_config_file)
        self.hostname = 'compute-dev-client-1'
        self.splunk_server = splunk_server
        self.username = username
        self.password = password


    def resolve_host_from_splunk_config(self, config_file):
        find_host_config = re.compile(r'host\s*=\s*(\S+)')
        with open(config_file) as fh:
            for line in fh:
                match = find_host_config.match(line)
                if match:
                    return match.group(1)
        raise LookupError('Cannot find "host" config key in %s' % ( config_file ))

    def collect(self):
        splunk_conn = splunk_connect(username=self.username, password=self.password, host=self.splunk_server)
        socket.setdefaulttimeout(None)
        query = 'search index=prod_ris_syslog earliest_time=-1h host=' + self.hostname + ' | stats count'
        response = splunk_conn.jobs.oneshot(query)

        splunk_counter = CounterMetricFamily('splunk_messages', 'Splunk message stats for this host', labels=['name'])
        for result in splunk_results_parser.ResultsReader(response):
            # should only be one row of results
            splunk_counter.add_metric(['last_hour'], result['count'])

        yield splunk_counter


# Format of this file is:
# user = <username>
# pass = <password>
# host = <hostname>
def get_splunk_query_config(filename):
    kv_regex = re.compile(r'(\w+)\s*=\s*(.*)')
    values = { }
    with open(filename) as fh:
        for line in fh:
            match = kv_regex.match(line)
            if match:
                values[match.group(1)] = match.group(2)

    return values['user'], values['pass'], values['host']


def main():
    start_http_server(prometheus_exporter_port)
    REGISTRY.register(NetDevCollector(expected_net_dev_name))

    splunk_query_user, splunk_query_password, splunk_query_hostname = get_splunk_query_config(splunk_query_config_file)
    REGISTRY.register(SplunkStatsCollector(splunk_config_file=splunk_config_file,
                                           splunk_server=splunk_query_hostname,
                                           username=splunk_query_user,
                                           password=splunk_query_password))
    while True:
        time.sleep(loop_sleep_time_seconds)

if __name__ == '__main__':
    # Become a daemon process
    try:
        pid = os.fork()
        if pid > 0:
            # In parent process, exit
            sys.exit(0)
    except OSError as e:
        sys.stderr.write("fork() failed: %d (%s)\n" % ( e.errno, e.splunkforwarder))
        sys.exit(1)

    try:
        pid = os.fork()
        if pid > 0:
            # Second parent process
            sys.stderr.write("Metrics daemon PID %d\n" % ( pid ))
            sys.exit(0)
    except OSError as e:
        sys.stderr.write("fork() failed: %d (%s)\n" % ( e.errno, e.splunkforwarder))
        sys.exit(1)

    main()
