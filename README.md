[![Gitter chat](https://img.shields.io/badge/gitter-join%20chat-brightgreen.svg)](https://gitter.im/CiscoSecurity/AMP-for-Endpoints "Gitter chat")

### AMP for Endpoints find duplicate GUIDs:

Looks through the computers in an environment and finds duplicate GUIDs based on MAC address.

### Before using you must update the following:
The authentictaion parameters are set in the ```api.cfg``` :
- client_id 
- api_key

### Usage:
```
python find_duplicate_guids.py
```

### Example script output:
```
python find_duplicate_guids.py
GUIDs found in environment: 14
Hosts with duplicate GUIDs found: 2

John's Laptop has 2 duplicates
                GUID                           LAST SEEN
  5f9b8897-d022-4b4b-bb3d-f90a14b9f603 - 2018-11-17T02:59:31Z
  a5eb905c-3fa2-4e9d-b9ec-93e92b359153 - 2018-11-17T02:17:12Z

WIN-PID1G1FX has 3 duplicates
                GUID                           LAST SEEN
  4cd3df7e-06b0-46ee-84ba-ef93dfda4cf1 - 2018-11-05T20:34:47Z
  698ec91e-6adc-41cf-9d5d-efd86cd6b2fc - 2018-11-05T20:32:11Z
  c973de42-a4ea-4238-b2b1-bcbb7f1ff0d8 - 2018-11-05T20:29:05Z
```
