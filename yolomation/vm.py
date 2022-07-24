import asyncio
import re
import random
import aiohttp
import logging
import os


word_file = "/usr/share/dict/words"
profanity = ["fucking", "shitting", "belching", "humping"]
callbacks_lock = asyncio.Lock()
callbacks = {}

class Callback:
    def __init__(self):
        self.event = asyncio.Event()
        self.value = None

        
def random_name():
    words = open(word_file).read().splitlines()
    pattern = re.compile('[^A-Za-z0-9]+')
    return random.choice(profanity) + "-" + "-".join(pattern.sub('', w).lower() for w in random.sample(words, 3))


async def create():
    name = random_name()
    await api_create_vm(name)
    event = await add_callback(name)
    await event.wait()
    async with callbacks_lock:
        value = callbacks[name].value
        del callbacks[name]
    return value


async def add_callback(name):
    async with callbacks_lock:
        callbacks[name] = Callback()
        return callbacks[name].event
        

async def execute_callback(name, value):
    async with callbacks_lock:
        if name not in callbacks:
            return
        
        callbacks[name].value = value
        callbacks[name].event.set()

        
async def api_create_vm(name):
    logging.info(f"Creating VM {name}")
    username = os.environ['VSPHERE_USERNAME']
    password = os.environ['VSPHERE_PASSWORD']
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession() as session:
        session_id = None
        template = None
        async with session.post('https://vcenter.yolocation.lan/rest/com/vmware/cis/session', auth=auth, verify_ssl=False) as resp:
            payload = await resp.json()
            if "value" in payload:
                session_id = payload["value"]
            else:
                logging.warning("no session")
                return
        async with session.get('https://vcenter.yolocation.lan/rest/com/vmware/content/library/item?library_id=3e3b8097-1f88-4a95-ac5a-87289211d6d5', headers={"vmware-api-session-id": session_id}, verify_ssl=False) as resp:
            payload = await resp.json()
            if "value" in payload:
                template = payload["value"][0]
            else:
                logging.warning("no template")
                return
        payload = {
            "description": "",
            "disk_storage": {
                "datastore": "datastore-16",
                "storage_policy": {
                    "policy": "",
                    "type": "USE_SPECIFIED_POLICY"
                }
            },
            "disk_storage_overrides": {},
            "guest_customization": {
                "name": "yolomation linux"
            },
            "name": name,
            "placement": {
                "cluster": "domain-c8",
                "folder": "group-v2005"
            },
            "powered_on": True,
            "vm_home_storage": {
                "datastore": "datastore-16",
                "storage_policy": {
                    "policy": "",
                    "type": "USE_SPECIFIED_POLICY"
                }
            }
        }
        async with session.post(
                f"https://vcenter.yolocation.lan/api/vcenter/vm-template/library-items/{template}?action=deploy",
                json=payload,
                verify_ssl=False,
                headers={"vmware-api-session-id": session_id}
        ) as resp:
            # This is VM ID
            payload = await resp.json()
            logging.info(f"VM {name} created: {payload}")
