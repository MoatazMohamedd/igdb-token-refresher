# IGDB token refresher

`refresh_igdb_token.py` gets a fresh Twitch client-credentials token and writes it as the `IGDB_ACCESS_TOKEN` GitHub Actions secret in every repository listed in `IGDB_REPOSITORIES`.

It never writes tokens to disk or logs their values.

## One-time setup

1. Create a GitHub fine-grained personal access token that has **Actions secrets: Read and write** permission for both target repositories. Store it as `GITHUB_TOKEN` in the environment running this script.
2. Store the Twitch app credentials as `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` there too. Do not put them in this repository.
3. Set `IGDB_REPOSITORIES` to comma-separated `OWNER/REPOSITORY` names.

For PowerShell, a local dry run looks like this (values below are placeholders):

```powershell
$env:TWITCH_CLIENT_ID = 'your-client-id'
$env:TWITCH_CLIENT_SECRET = 'your-client-secret'
$env:GITHUB_TOKEN = 'github-fine-grained-pat'
$env:IGDB_REPOSITORIES = 'owner/first-repo,owner/second-repo'
python -m pip install -r requirements.txt
python refresh_igdb_token.py --dry-run
```

Remove `--dry-run` once it prints the expected repository names. A successful run prints only expiry information and confirmation of each secret update.
