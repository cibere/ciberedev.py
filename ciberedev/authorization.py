from typing import Optional


class FileUploaderAuthorization:
    def __init__(self, *, token: Optional[str] = None):
        self.token = token


class Authorization:
    file: FileUploaderAuthorization

    def __init__(
        self,
        *,
        file_uploader: FileUploaderAuthorization = FileUploaderAuthorization(),
    ):
        self.file = file_uploader
