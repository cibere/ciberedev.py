# Update Log

## 0.4.2

**Breaking Changes**

- `ciberedev.client.Client.take_screenshot` now returns a `ciberedev.file.File` object, and `ciberedev.Screenshot` has been removed
- In the same update it was added, it's removed. `ciberedev.checkers` is removed in preparation for future api changes

**Minor Changes**

- Added `minor changes` to update log
- `ciberedev.client.Client.latency` now only gets updated when `ciberedev.client.Client.ping` gets called

**Additions**

- _Added support for checkers endpoint at `ciberedev.checkers`_
- `update` and `open-docs` CLI commands
- Added `ciberedev.file.File`
- Added support for `random/word` endpoint at `ciberedev.client.Client.get_random_words`
- Added support for `image/ascii` endpoint at `ciberedev.client.Client.convert_image_to_ascii`
- made `HTTPClient.ping` public via `ciberedev.client.Client.ping`

**Bug Fixes**

- Miss-leading name for `ClientNotStarted`, and it has been renamed to `ClientAlreadyClosed`
- Fixed bug where `get_search_results` would check for status code 200 twice instead of 200 then 400
- Fixed bug where importing ciberedev will always error due to it not finding `ciberedev.types`

## 0.4.1

**Breaking Changes**

- None

**Minor Changes**

- None

**Additions**

- CLI Commands such as `system-info` and `version`

**Bug Fixes**

- Fixed bug where `ciberedev.client.Client.take_screenshot` does not validate the url
- Fixed bug where `ciberedev.client.Client.take_screenshot` makes a request to an invalid endpoint

## 0.4.0

**Breaking Changes**

- `Client.search` got renamed to `ciberedev.client.Client.get_search_results`

**Minor Changes**

- None

**Additions**

- Addition of `ciberedev.client.Client.on_ratelimit`

**Bug Fixes**

- None
