#!/usr/bin/python

import re
import sys
import os
import time
import traceback
import socket

sys.path.insert(0, os.path.join( os.path.dirname(__file__), '/splunklibs/lib/python2.7/site-packages'))
from splunklib.client import connect as splunk_connect
import splunklib.results as splunk_results_parser

splunk_config_file = '/opt/splunkforwarder/etc/apps/SplunkUniversalForwarder/local/inputs.conf'
loop_sleep_time_seconds = 60
expected_net_dev_name = 'eth0'
splunk_search_hostname = 'machinedata.wustl.edu'
metrics_output_file = '/var/lib/prometheus/textfile/splunk_forwarder.prom'

def resolve_host_from_splunk_config(config_file):
    find_host_config = re.compile(r'host\s*=\s*(\S+)')
    with open (config_file) as fh:
        for line in fh:
            match = find_host_config.match(line)
            if match:
                return match.group(1)
    raise LookupError('Cannot find "host" config key in %s' % ( config_file ))

def collect_stats_for_netdev(name):
    find_name = re.compile(r'\s*' + name + r':')
    extract_stats = re.compile(r':\s+(?P<rx_bytes>\d+)\s+(?P<rx_packets>\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(?P<tx_bytes>\d+)\s+(?P<tx_packets>\d+)')
    with open('/proc/net/dev') as fh:
        for line in fh:
            if find_name.match(line):
                match = extract_stats.search(line)
                if match:
                    return { k: match.group(k) for k in ['rx_bytes', 'rx_packets','tx_bytes','tx_packets'] }
                else:
                    raise ValueError('Could not extract tx/tx packets and bytes from /proc/net/dev for device ' + name)
    raise LookupError('Could not find device named ' + name + ' in /proc/net/dev')

def collect_message_stats_from_splunk(my_hostname, splunk_server, username, password):
    service = splunk_connect(username=username, password=password, host=splunk_server)
    socket.setdefaulttimeout(None)
    query = 'search index=prod_ris_syslog earliest_time=-1h host=' + my_hostname + ' | stats count'
    response = service.jobs.oneshot(query)

    for result in splunk_results_parser.ResultsReader(response):
        # Should only be one row of results
        return { 'messages_last_hour': result['count'] }

def record_metrics(metrics_file, net_stats, msg_stats):
    next_metrics_filename = metrics_file + '.next'
    with open(next_metrics_filename, 'w') as fh:
        fh.write('splunk_forwarder_transmit_bytes '   + net_stats['tx_bytes'] + "\n")
        fh.write('splunk_forwarder_transmit_packets ' + net_stats['tx_packets'] + "\n")
        fh.write('splunk_forwarder_receive_bytes '    + net_stats['rx_bytes'] + "\n")
        fh.write('splunk_forwarder_receive_packets '  + net_stats['rx_packets'] + "\n")
        fh.write('splunk_forwarder_host_messages_last_hour ' + msg_stats['messages_last_hour'] + "\n")
        fh.write('splunk_forwarder_timestamp ' + str(int(time.time())) + "\n")

    os.rename(next_metrics_filename, metrics_file)

def main():
    host = resolve_host_from_splunk_config(splunk_config_file)

    while True:
        try:
            net_stats = collect_stats_for_netdev(expected_net_dev_name)
            msg_stats = collect_message_stats_from_splunk(my_hostname=host,
                                                          splunk_server=splunk_search_hostname,
                                                          username='ris-api',
                                                          password='TRGZnUaJFUcrFY5sXzwSFrPn')

            record_metrics(metrics_output_file, net_stats, msg_stats)

        except Exception as e:
            sys.stderr.write('Caught exception during main loop:\n')
            sys.stderr.write(traceback.format_exc())

        time.sleep(loop_sleep_time_seconds)


if __name__ == '__main__':
    main()
