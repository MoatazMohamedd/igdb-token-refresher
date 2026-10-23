# IGDB token refresher

`refresh_igdb_token.py` gets a fresh Twitch client-credentials token and writes it as the `IGDB_ACCESS_TOKEN` GitHub Actions secret in every repository listed in `IGDB_REPOSITORIES`.

It never writes tokens to disk or logs their values.

## GitHub Actions manual run

This repository includes a manual workflow at `.github/workflows/refresh-igdb-token.yml`. Before running it, add these values in this repository's **Settings → Secrets and variables → Actions**:

| Type | Name | Value |
| --- | --- | --- |
| Secret | `TWITCH_CLIENT_ID` | Your Twitch application client ID |
| Secret | `TWITCH_CLIENT_SECRET` | Your Twitch application client secret |
| Secret | `TOKEN_GITHUB` | A fine-grained PAT with **Actions secrets: Read and write** access to both target repositories |
| Variable | `IGDB_REPOSITORIES` | Comma-separated `OWNER/REPOSITORY` names, for example `owner/app-one,owner/app-two` |

Then open the repository's **Actions** tab, select **Refresh IGDB access token**, choose **Run workflow**, and run it. You may optionally enter a repository list for that run only, or select dry-run to validate the configuration without updating secrets.

`TOKEN_GITHUB` must be a separate PAT: the automatic `GITHUB_TOKEN` issued to this workflow does not have access to secrets in other repositories.

## One-time setup for a non-GitHub runner

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
