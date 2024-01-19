import bloock
from bloock.client.integrity import IntegrityClient
from bloock.client.record import RecordClient
from bloock.entity.integrity.network import Network
 
from bloock.client.availability import AvailabilityClient
from bloock.entity.availability.ipfs_loader import IpfsLoader
from bloock.entity.availability.ipfs_publisher import IpfsPublisher

import json

from encrypt import encrypt_data

from encrypt import encrypt_data

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def send(name,uuid,decision):
    # we set the API key and create a client
    bloock.api_key = os.getenv("API_KEY") 
    record_client = RecordClient()
    integrity_client = IntegrityClient()
    availability_client = AvailabilityClient()

    dict_={"name": encrypt_data(name),
            "uuid": uuid,
            "decision": encrypt_data(decision.upper())
            }
    
    
    # Convert the dictionary to a JSON string
    json_string = json.dumps(dict_)

    # and build a record from it
    record = record_client.from_json(json_string).build()
    file_uuid = availability_client.publish(record, IpfsPublisher())
 
    records = [record]
   
    #send data and get receipts
    send_receipts = integrity_client.send_records(records)
    #return send_receipts[0].anchor,file_uuid
    