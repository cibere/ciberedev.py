class SearchResult:
    def __init__(self, *, data: dict):
        self.title = data["title"]
        self.description = data["description"]
        self.url = data["url"]
