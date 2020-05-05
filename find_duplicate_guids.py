from collections import namedtuple
import configparser
import json
import requests

def process_response_json(response_json, parsing_container):
    '''Process the decoded JSON blob from /v1/computers API Endpoint
    '''

    def process_guid_json(guid_json, parsing_container=parsing_container):
        '''Process the individual GUID entry
        '''
        connector_guid = guid_json.get('connector_guid')
        hostname = guid_json.get('hostname')
        last_seen = guid_json.get('last_seen')
        network_addresses = guid_json.get('network_addresses')

        parsing_container.setdefault(hostname, {'macs':[], 'mac_guids':{}, 'guid_last_seen':{}})
        parsing_container[hostname]['guid_last_seen'][connector_guid] = last_seen

        for network_interface in network_addresses:
            mac = network_interface.get('mac')
            # ip = network_interface.get('ip')
            # ipv6 = network_interface.get('ipv6')

            parsing_container[hostname]['macs'].append(mac)
            parsing_container[hostname]['mac_guids'].setdefault(mac, set())
            parsing_container[hostname]['mac_guids'][mac].add(connector_guid)

    for guid_entry in response_json['data']:
        if 'network_addresses' in guid_entry:
            process_guid_json(guid_entry)

def analyze_parsed_computers(parsed_data, duplicate_container):
    ''' Analyzes the parsed_computers container and looks at how many times each MAC Address
        appears for a given hostname. If the same MAC appears more than once the host is
        added to  the duplicate_computers container.
    '''
    for hostname, data in parsed_data.items():
        macs = data['macs']
        for mac in macs:
            if macs.count(mac) > 1:
                for guid in data['mac_guids'][mac]:
                    host_tuple = namedtuple('host_tuple', ['hostname', 'guid', 'last_seen'])
                    last_seen = parsed_data[hostname]['guid_last_seen'][guid]
                    duplicate_container.add(host_tuple(hostname, guid, last_seen))

def format_duplicate_output(duplicate_container):
    ''' Processes the duplicate_computers container and formats the output based on hostname
        Returns a dictionary that can be saved to disk as JSON
    '''
    hosts = {}
    for host_tuple in sorted(duplicate_container):
        hostname = host_tuple.hostname
        guid = host_tuple.guid
        last_seen = host_tuple.last_seen
        hosts.setdefault(hostname, {})
        hosts[hostname][guid] = last_seen
    return hosts

def print_duplicate_output(formatted_duplicate_container):
    '''Process formatted_duplicate_computers and print duplicate stats by host name
    '''
    print('Hosts with duplicate GUIDs found: {}'.format(len(formatted_duplicate_container)))
    for host, dupes in formatted_duplicate_container.items():
        print('\n{} has {} duplicates'.format(host, len(dupes)))
        print('{:>20}{:>36}'.format('GUID', 'LAST SEEN'))
        for guid, last_seen in dupes.items():
            print('  {} - {}'.format(guid, last_seen))

def write_duplicate_json(formatted_duplicate_container):
    '''Write formatted_duplicate_computers to disk as JSON
    '''
    with open('duplicate_hosts.json', 'w') as file:
        file.write(json.dumps(formatted_duplicate_container))

def write_parsed_computers(parsed_data):
    ''' Converts the Set of unique MAC Addresses in the parsed_computers container
        Without this conversion it can not be written to disk as JSON
        Writes parsed computers to disk as JSON
    '''
    for _, data in parsed_data.items():
        for key, _ in data['mac_guids'].items():
            data['mac_guids'][key] = list(data['mac_guids'][key])

    with open('parsed_computers.json', 'w') as file:
        file.write(json.dumps(parsed_data))

def get(session, url):
    '''HTTP GET the URL and return the decoded JSON
    '''
    response = session.get(url)
    response_json = response.json()
    return response_json

def main():
    '''The main logic of the script
    '''

    # Specify the config file
    config_file = 'api.cfg'

    # Reading the config file to get settings
    config = configparser.RawConfigParser()
    config.read(config_file)
    client_id = config.get('AMPE', 'client_id')
    api_key = config.get('AMPE', 'api_key')

    # Instantiate requestions session object
    amp_session = requests.session()
    amp_session.auth = (client_id, api_key)

    # Containers for data
    parsed_computers = {}
    duplicate_computers = set()

    # URL to query AMP
    computers_url = 'https://api.amp.cisco.com/v1/computers'

    # Query the API
    response_json = get(amp_session, computers_url)

    # Print the total number of GUIDs found
    total_guids = response_json['metadata']['results']['total']
    print('GUIDs found in environment: {}'.format(total_guids))

    # Process the returned JSON
    process_response_json(response_json, parsed_computers)

    # Check if there are more pages and repeat
    while 'next' in response_json['metadata']['links']:
        next_url = response_json['metadata']['links']['next']
        response_json = get(amp_session, next_url)
        index = response_json['metadata']['results']['index']
        print('Processing index: {}'.format(index))
        process_response_json(response_json, parsed_computers)

    analyze_parsed_computers(parsed_computers, duplicate_computers)

    formatted_duplicate_computers = format_duplicate_output(duplicate_computers)

    print_duplicate_output(formatted_duplicate_computers)

    write_duplicate_json(formatted_duplicate_computers)

if __name__ == "__main__":
    main()
