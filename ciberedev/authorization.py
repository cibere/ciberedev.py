from typing import Optional


class FileUploaderAuthorization:
    def __init__(self, *, token: Optional[str] = None):
        self.token = token


class ScreenshotAuthorization:
    def __init__(self, *, token: Optional[str] = None):
        self.token = token


class Authorization:
    def __init__(
        self,
        *,
        screenshot: Optional[ScreenshotAuthorization] = ScreenshotAuthorization(),
        file_uploader: Optional[
            FileUploaderAuthorization
        ] = FileUploaderAuthorization(),
    ):
        self.screenshot = screenshot
        self.file = file_uploader
