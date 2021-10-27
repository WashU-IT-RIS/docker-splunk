#!/usr/bin/python

import re
import sys
import time
import traceback

splunk_config_file = '/opt/splunkforwarder/etc/apps/SplunkUniversalForwarder/local/inputs.conf'
loop_sleep_time_seconds = 60

def resolve_host_from_splunk_config(config_file):
    find_host_config = re.compile(r'host\s*=\s*(\S+)')
    with open (config_file) as fh:
        for line in fh:
            match = find_host_config.match(line)
            if match:
                return match.group(1)
    raise LookupError('Cannot find "host" config key in %s' % ( config_file ))

# Assumes the container has a 'lo' and one other net device
def resolve_net_device():
    netdev_find = re.compile(r'\s*(\w+):')
    devices_found = { }
    with open('/proc/net/dev') as fh:
        # There are two header lines
        header = fh.readline()
        header = fh.readline()
        for line in fh:
            match = netdev_find.match(line)
            if match:
                dev_name = match.group(1)
                devices_found[dev_name] = True

    # Don't care about the loopback device
    devices_found.pop('lo', None)

    device_names = devices_found.keys()
    if len(device_names) > 1:
        raise LookupError('Found more than one non-loopback network device: %s' % ( device_names ))

    return device_names[0]

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

def collect_message_stats_from_splunk(host):
    pass

def main():
    host = resolve_host_from_splunk_config(splunk_config_file)
    netdev = resolve_net_device()

    while True:
        try:
            net_stats = collect_stats_for_netdev(netdev)
            msg_stats = collect_message_stats_from_splunk(host)

        except Exception as e:
            sys.stderr.write('Caught exception during main loop:\n')
            sys.stderr.write(traceback.format_exc())

        time.sleep(loop_sleep_time_seconds)


if __name__ == '__main__':
    main()
