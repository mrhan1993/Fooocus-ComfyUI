"""
This is an example that uses the websockets api and the SaveImageWebsocket node
to get images directly without them being saved to disk
# NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
"""
import json
import uuid
from typing import Dict

import requests
import websocket

from tools.logger import common_logger


class Execute:
    def __init__(self, server_address: str, client_id: str = str(uuid.uuid4())):
        """
        Initialize an Execute instance.
        :param server_address: IP addr for execute task
        :param client_id: a unique string identifier
        """
        self.client_id = client_id
        self.server_address = server_address

    def queue_prompt(self, prompt: Dict) -> Dict:
        """
        Queue a prompt for execution.
        :param prompt: The prompt to execute.
        :return: The response from the server.
        """
        url = f"http://{self.server_address}/prompt"
        data = {"prompt": prompt, "client_id": self.client_id}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            common_logger.error(f"[Execute] Error executing prompt: {e}")

    def get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """
        Get an image from the server.
        :param filename: The name of the image file.
        :param subfolder: The subfolder containing the image.
        :param folder_type: The type of folder.
        :return: The image data as bytes.
        """
        url = f"http://{self.server_address}/view"
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.content
        except Exception as e:
            common_logger.error(f"[Execute] Error getting image: {e}")

    def get_history(self, prompt_id: str) -> Dict:
        """
        Get the execution history for a prompt.
        :param prompt_id: The ID of the prompt.
        :return: The history data.
        """
        url = f"http://{self.server_address}/history/{prompt_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            common_logger.error(f"[Execute] Error getting history: {e}")

    def get_images(self, ws: websocket.WebSocket, prompt: Dict) -> Dict:
        """
        Get images from the WebSocket connection.
        :param ws: The WebSocket connection.
        :param prompt: The prompt to execute.
        :return: A dictionary of node names to lists of image data.
        """
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        current_node = ""

        while True:
            try:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['prompt_id'] == prompt_id:
                            if data['node'] is None:
                                break  # Execution is done
                            current_node = data['node']
                elif current_node == 'save_image_websocket_node':
                    output_images[current_node].append(out[8:])
            except Exception as e:
                common_logger.error(f"[Execute] WebSocket error: {e}")
                break
        return output_images

    def execute(self, workflow: Dict) -> Dict:
        """
        Run a workflow and get the resulting images.
        :param workflow: The workflow to execute.
        :return: A dictionary of node names to lists of image data.
        """
        ws_url = f"ws://{self.server_address}/ws?clientId={self.client_id}"
        try:
            with websocket.create_connection(ws_url) as ws_client:
                return self.get_images(ws_client, workflow)
        except Exception as e:
            common_logger.error(f"[Execute] WebSocket error: {e}")
            return {}
