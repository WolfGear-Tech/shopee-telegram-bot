import json

import requests
from stela import settings


class PixService:
    def __init__(self) -> None:
        self.api_key = settings["PIX_API_KEY"]
        self.base_url = settings["project.pix_url"]

    def generate_qr_code(self, amount, description, reference):
        endpoint = "/pix/qrcode/generate"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"amount": amount, "description": description, "reference": reference}
        response = requests.post(self.base_url + endpoint, headers=headers, data=json.dumps(data), timeout=5)
        if response.status_code == 200:
            return response.json()["qr_code"]
        else:
            raise Exception("Failed to generate QR code")

    def get_transaction_status(self, transaction_id):
        endpoint = f"/pix/transaction/{transaction_id}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        response = requests.get(self.base_url + endpoint, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()["status"]
        else:
            raise Exception("Failed to get transaction status")
