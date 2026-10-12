import json
import urllib.request
from urllib.error import HTTPError, URLError


def find_oldest_year(
    payload: dict,
    name: str,
    version: str,
    oldest_year: int | None,
    oldest_pinned_release: str,
) -> tuple[int | None, str]:
    urls = payload.get("urls", [])
    if not urls:
        return oldest_year, oldest_pinned_release

    upload_time = urls[0].get("upload_time_iso_8601") or urls[0].get("upload_time")
    if not upload_time:
        return oldest_year, oldest_pinned_release

    release_year = int(upload_time[:4])
    if oldest_year is None or release_year < oldest_year:
        return release_year, f"{name}=={version} ({release_year})"

    return oldest_year, oldest_pinned_release


def readReq(input_file: str = "requirements.txt") -> tuple[int, int, int, str]:
    dependencies_checked = 0
    packages_not_found = 0
    version_not_matched = 0
    olden_pinned_release = "None"
    oldest_year = None

    with open(input_file, "r", encoding="utf-8") as source:
        for raw_line in source:
            line = raw_line.strip()

            name, version = [part.strip() for part in line.split("==", 1)]
            version_url = f"https://pypi.org/pypi/{name}/{version}/json"

            try:
                with urllib.request.urlopen(version_url) as response:
                    payload = json.load(response)
                    # print(payload)
                dependencies_checked += 1

                oldest_year, olden_pinned_release = find_oldest_year(
                    payload,
                    name,
                    version,
                    oldest_year,
                    olden_pinned_release,
                )

            except HTTPError as exc:
                if exc.code == 404:
                    package_url = f"https://pypi.org/pypi/{name}/json"
                    try:
                        with urllib.request.urlopen(package_url) as response:
                            json.load(response)
                        version_not_matched += 1
                    except (HTTPError, URLError):
                        packages_not_found += 1
                else:
                    packages_not_found += 1

            except URLError:
                packages_not_found += 1

    return (
        dependencies_checked,
        packages_not_found,
        version_not_matched,
        olden_pinned_release,
    )


def main() -> None:
    (
        dependencies_checked,
        packages_not_found,
        version_not_matched,
        oldest_pinned_release,
    ) = readReq()
    print(f"Dependencies Checked : {dependencies_checked}")
    print(f"Packages not on PyPi : {packages_not_found}")
    print(f"Versions not on PyPi : {version_not_matched}")
    print(f"Oldest Pinned Release : {oldest_pinned_release}")


if __name__ == "__main__":
    main()
