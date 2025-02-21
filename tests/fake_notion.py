# tests/fake_notion.py

# Define a fake pages class to simulate Notion API behavior.
class FakePages:
    def __init__(self):
        self.last_update = None
        self.last_retrieve = None

    def update(self, page_id, properties=None, archived=None):
        # Store the update call for later verification.
        self.last_update = {"page_id": page_id, "properties": properties, "archived": archived}
        # On a successful update, return a dummy success response.
        return {"status": "success"}

    def retrieve(self, page_id):
        self.last_retrieve = page_id
        # By default, simulate a page that is not archived.
        return {"archived": False}

# A fake Notion client containing our fake pages.
class FakeNotionClient:
    def __init__(self):
        self.pages = FakePages()