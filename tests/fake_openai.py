# tests/fake_openai.py

class FakeMessage:
    def __init__(self, content):
        self.content = content

class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)

class FakeResponse:
    def __init__(self, content):
        # Simulate a response with a single choice.
        self.choices = [FakeChoice(content)]
