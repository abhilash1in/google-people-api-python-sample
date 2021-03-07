import pickle
import os.path
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", level=logging.WARNING
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# set DRY_RUN to False to actually copy
DRY_RUN = True

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/contacts.other.readonly",
    "https://www.googleapis.com/auth/contacts",
]


def get_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def get_contact_groups(contact_groups_service):
    request = contact_groups_service.list()
    response = request.execute()
    return response.get("contactGroups", [])


def get_contacts(people_service, pageSize=100):
    request = people_service.connections().list(
        resourceName="people/me", pageSize=pageSize, personFields="names,emailAddresses,phoneNumbers"
    )
    contacts = []
    while request is not None:
        response = request.execute()
        contacts.extend(response.get("connections", []))
        request = people_service.connections().list_next(request, response)
    return contacts


def get_other_contacts(other_contacts_service, pageSize=100):
    request = other_contacts_service.list(pageSize=pageSize, readMask="names,emailAddresses,phoneNumbers")
    other_contacts = []
    while request is not None:
        response = request.execute()
        other_contacts.extend(response.get("otherContacts", []))
        request = other_contacts_service.list_next(request, response)
    return other_contacts


def get_contacts_with_name_and_phone_number(contacts):
    result = []
    for contact in contacts:
        if contact.get("names") and contact.get("phoneNumbers"):
            result.append(contact)
    return result


def copy_contact(
    resource_name,
    other_contacts_service,
    body={"copyMask": "names,emailAddresses,phoneNumbers"},
):
    copied_contact = other_contacts_service.copyOtherContactToMyContactsGroup(
        resourceName=resource_name, body=body
    ).execute()
    return copied_contact


def delete_contact(people_service, resource_name):
    response = people_service.deleteContact(resourceName=resource_name).execute()
    return response


def delete_other_contact(other_contacts_service, resource_name):
    # TODO: https://stackoverflow.com/questions/66512264/delete-other-contact-using-python-with-google-people-api
    pass


def main():
    creds = get_creds()

    people_api = build("people", "v1", credentials=creds)

    contact_groups_service = people_api.contactGroups()
    contact_groups = get_contact_groups(contact_groups_service=contact_groups_service)
    logger.info(f"Found {len(contact_groups)} contact groups")

    people_service = people_api.people()
    contacts = get_contacts(people_service=people_service)
    logger.info(f"Found {len(contacts)} contacts")

    other_contacts_service = people_api.otherContacts()
    other_contacts = get_other_contacts(other_contacts_service=other_contacts_service)
    logger.info(f'Found {len(other_contacts)} contacts in "Other Contacts"')

    valid_other_contacts = get_contacts_with_name_and_phone_number(contacts=other_contacts)
    logger.info(f'Found {len(valid_other_contacts)} contacts in "Other Contacts" with name and phone number')

    for index, contact in enumerate(valid_other_contacts):
        resource_name = contact.get("resourceName")
        names = contact.get("names")
        phone_numbers = contact.get("phoneNumbers")

        # FIXME: possible IndexError for names[0]
        logger.info(f'{index + 1}. Copying {names[0].get("displayName")} (Resource name: {resource_name})')

        if not DRY_RUN:
            copied_contact = copy_contact(resource_name, other_contacts_service)

            copied_names = copied_contact.get("names", [])
            # FIXME: possible IndexError for copied_names[0]
            copied_display_name = copied_names[0].get("displayName")

            logger.info(f"{copied_display_name} copied from Other Contacts to My Contacts group")

    # Sample delete op
    # response = delete_contact(people_service=people_service, resource_name='people/c1971897568350947761')


if __name__ == "__main__":
    main()
