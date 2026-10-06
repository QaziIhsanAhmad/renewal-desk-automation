# Renewal Desk: one-year daily posting package

STATUS: ACTIVE. Authenticated read-only check and first live scheduling completed on 6 October 2026. Buffer confirmed three scheduled posts for 10–12 October 2026, at 20:00 Asia/Karachi. Publication and revenue remain unverified.

365 dated Pins, 10 October 2026 to 9 October 2027 inclusive. Includes 365 original 1000x1500 typographic PNG cards and distinct descriptions. Rotates 52 subscription-review topics and seven review prompts. This is a repeatable editorial series, not 365 unrelated articles. All links go directly to the existing Gumroad kit. No promised savings, sales, income, automatic cancellation or reminders.

The standard-library Python worker runs daily at 09:17 Pakistan time using GitHub Actions, keeping at most seven days ahead and respecting a maximum of ten scheduled Buffer posts. Each Pin is scheduled for 20:00 Pakistan time. It skips any day occupied by an existing scheduled/sent/sending Buffer post, stops on recent failed posts, avoids automatic mutation retries, and stops creating posts after the calendar ends. Existing native Pinterest posts for 7–9 October are outside this package. Native Pinterest posts are not visible to the Buffer API: do not add another native posting schedule for dates covered here.

## Owner setup required
1. This package is installed in the dedicated public repository QaziIhsanAhmad/renewal-desk-automation. The Prepare yearly Pin images workflow builds and commits all 365 images on initial source upload. Check that job succeeds before Buffer activation.
2. Host `media/` at a public HTTPS URL. A public GitHub repository's raw-file directory can be used, or existing owner-authorized public hosting. The public media base is already configured in the daily workflow. A private repository's raw URLs will not work.
3. In Buffer's API settings create a personal API key. Store it directly in GitHub repository Settings → Secrets and variables → Actions → New repository secret, named `BUFFER_API_KEY`. Never commit it or send it in chat. Creating a key or authorizing secret storage must be approved by the owner.
4. The worker automatically uses the organization/board only when exactly one is available. Otherwise set `BUFFER_ORGANIZATION_ID` and `BUFFER_BOARD_ID` to the correct organization and existing Subscription Planning & Renewal Checklists board service ID.
5. Run Actions → Renewal Desk daily refill with `check_only=true`, confirm the right channel/board/assets and proposed dates, then run with `check_only=false`. Verify the actual Buffer queue and the first public Pin after publication. Initial authenticated read-only and live scheduling tests passed on 6 October 2026.

## Operational limits
Buffer's free queue is finite; this worker replenishes it. No paid API or AI generation runs daily. GitHub usage, account limits and availability must be checked before activation: public repositories normally get free standard hosted runners, private plans have quotas. Never enable paid overages. Scheduled jobs can be delayed and public-repository schedules can be disabled after inactivity; a one-year unattended guarantee is not provided. Review platform notifications and recover failures when alerted. The worker does not count visitors or revenue, and a scheduled Pin is not proof of publication or sales.

Local checks: `python -m unittest test_refill.py`; calendar has 365 contiguous dates, valid length-limited fields and all image assets. The API implementation follows Buffer's current documented schema and passed authenticated read-only and scheduling tests on 6 October 2026.

Official references: https://developers.buffer.com/ ; https://developers.buffer.com/reference.html ; https://buffer.com/pricing ; https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

The repository is QaziIhsanAhmad/renewal-desk-automation. Public media URL is configured automatically. The dedicated BUFFER_API_KEY secret is configured and the daily workflow is active. No AUTOMATION_ENABLED variable is required. To pause, disable the daily workflow in Actions. Inspect the first public Pin after publication.
