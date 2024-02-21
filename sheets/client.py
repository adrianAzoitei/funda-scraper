from typing import List
import os
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery
import httplib2
from googleapiclient.errors import HttpError
import sys
from pandas import DataFrame
import json

class GoogleSheetsClient(object):
    def __init__(self):
        self.scopes: List[str] = ["https://www.googleapis.com/auth/spreadsheets"]
        self.spreadsheet_id: str = os.environ["SHEET_ID"]
        self.range: str = "Bot!A:A"

    def _get_credential(self):
        """Creates a Credential object with the correct OAuth2 authorization.

        Uses the service account key stored in SERVICE_ACCOUNT_KEY_FILE.

        Returns:
            Credentials, the user's credential.
        """
        credential = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(os.environ["SERVICE_ACCOUNT_TOKEN"]),
            self.scopes
            )

        if not credential or credential.invalid:
            print('Unable to authenticate using service account key.')
            sys.exit()
        return credential

    def _get_service(self):
        """Creates a service endpoint for the zero-touch enrollment API.

        Builds and returns an authorized API client service for v1 of the API. Use
        the service endpoint to call the API methods.

        Returns:
            A service Resource object with methods for interacting with the service.
        """
        http_auth = self._get_credential().authorize(httplib2.Http())
        return discovery.build('sheets', 'v4', http=http_auth)

    def update(self, df: DataFrame) -> None:
        """
        Handles the main Google Sheet update function.
        """
        try:
            service = self._get_service()

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.spreadsheet_id, range=self.range)
                .execute()
            )
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return
            
            addresses = [row[0] for row in values]

            for _, row in df.iterrows():
                if row["address"] not in addresses:
                    values = [
                        [
                            f"=HYPERLINK(\"https://www.funda.nl/koop/{row['city']}/huis-{row['house_id']}-{row['address'].lower().replace(' ', '-')}/\"; \"{row['address']}\")",
                            row["price"],
                            "Beschikbaar",
                            row["energy_label"],
                            "=TODAY()",
                            row["city"].capitalize().replace("-", " ")
                        ],
                    ]
                    body = {"values": values}
                    result = (
                        service.spreadsheets()
                        .values()
                        .append(
                            spreadsheetId=self.spreadsheet_id,
                            range="Bot!A:C",
                            valueInputOption="USER_ENTERED",
                            body=body,
                        )
                        .execute()
                    )
                    print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
                else:
                    print(f"Saw {row['address']} before.")
        except HttpError as err:
            print(err)

