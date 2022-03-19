class Cache:
    def __init__(self) -> None:
        self.data = {}

    def is_in_cache(self, url: str):
        return url in self.data

    def add_to_cache(self, url: str, last_modied: str, etag: str, msg: str):
        self.data[url] = last_modied, etag, msg

    def get_data(self, url: str):
        return self.data[url]