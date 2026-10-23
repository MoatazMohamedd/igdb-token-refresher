#!/usr/bin/env python3
"""Refresh an IGDB/Twitch token and store it as a GitHub Actions secret."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from typing import Any

import requests
from nacl import encoding, public

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
GITHUB_API_URL = "https://api.github.com"
SECRET_NAME = "IGDB_ACCESS_TOKEN"


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} must be set")
    return value


def get_igdb_token(client_id: str, client_secret: str) -> str:
    response = requests.post(
        TWITCH_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Twitch did not return an access_token")
    expires_in = payload.get("expires_in")
    print(f"Obtained a new Twitch token (expires in {expires_in} seconds).")
    return token


def github_request(method: str, path: str, github_token: str, **kwargs: Any) -> requests.Response:
    response = requests.request(
        method,
        f"{GITHUB_API_URL}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=30,
        **kwargs,
    )
    response.raise_for_status()
    return response


def encrypt_secret(value: str, key: str) -> str:
    public_key = public.PublicKey(key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def update_secret(repository: str, secret_value: str, github_token: str, dry_run: bool) -> None:
    if repository.count("/") != 1 or any(not part for part in repository.split("/")):
        raise RuntimeError(f"Invalid repository name: {repository!r}; use OWNER/REPOSITORY")

    if dry_run:
        print(f"Would update {SECRET_NAME} in {repository}.")
        return

    key_response = github_request(
        "GET", f"/repos/{repository}/actions/secrets/public-key", github_token
    ).json()
    encrypted_value = encrypt_secret(secret_value, key_response["key"])
    github_request(
        "PUT",
        f"/repos/{repository}/actions/secrets/{SECRET_NAME}",
        github_token,
        json={"encrypted_value": encrypted_value, "key_id": key_response["key_id"]},
    )
    print(f"Updated {SECRET_NAME} in {repository}.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Request a token but do not update GitHub.")
    args = parser.parse_args()

    try:
        repositories = [item.strip() for item in required_env("IGDB_REPOSITORIES").split(",") if item.strip()]
        if not repositories:
            raise RuntimeError("IGDB_REPOSITORIES must contain at least one OWNER/REPOSITORY")
        token = get_igdb_token(required_env("TWITCH_CLIENT_ID"), required_env("TWITCH_CLIENT_SECRET"))
        github_token = required_env("GITHUB_TOKEN")
        for repository in repositories:
            update_secret(repository, token, github_token, args.dry_run)
    except (RuntimeError, KeyError, requests.RequestException, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
