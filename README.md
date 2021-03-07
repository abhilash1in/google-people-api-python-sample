## Google People API Python Sample

This repo illustrates how to call a limited set of Google People APIs via their respective Python bindings.

The main intention of writing this was to scan all contacts in "Other Contacts" and copy them over to "myContacts" group if the contact in "Other Contacts" had a name and phone number associated with it (excluding contacts with only a name/email addresss).

Reference:
- Python [quickstart] (https://developers.google.com/people/quickstart/python)
- People API [REST reference] (https://developers.google.com/people/api/rest)
- google-api-python-client [People API library] (https://googleapis.github.io/google-api-python-client/docs/dyn/people_v1.html)
- google-api-python-client [core] (https://googleapis.github.io/google-api-python-client/docs/epy/index.html)