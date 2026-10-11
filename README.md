# Portfolio Website

Responsive portfolio built with plain HTML, CSS, and JavaScript.

## Structure

```text
portfolio_website/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── script.js
├── assets/
│   └── resume.pdf   # optional
└── README.md
```

## Run locally

Open `index.html` in a browser. No build tools or package installation are needed.

## Deploy to GitHub Pages

1. Upload the contents of this folder to your GitHub repository.
2. Open **Settings → Pages**.
3. Select **Deploy from a branch**, choose `main` and `/(root)`, then save.
4. Wait for GitHub Pages to publish.

## Replace the dummy content

Update the name, biography, coding profile usernames and URLs, email, LinkedIn URL, project details, repository links, skills, education, experience, and statistics in `index.html`.

The résumé button expects a PDF at `assets/resume.pdf`. Add your résumé there or remove the button.

## File roles

- `index.html`: page structure and content
- `css/style.css`: visual styling and responsive layout
- `js/script.js`: mobile menu behavior and copyright year


## Automatic competitive-programming ratings

The cards read `data/ratings.json`. GitHub Actions runs `.github/workflows/update-ratings.yml` every six hours and can be started manually from the **Actions** tab.

- **Codeforces:** official public API (`rating` and `maxRating`).
- **LeetCode:** public GraphQL contest ranking and contest history.
- **CodeChef:** community-maintained CodeChef Stats API; it is not an official CodeChef API and may change or become unavailable.

When a provider fails, the updater preserves the last successful values. If no values have ever been fetched, the page displays **Unavailable** rather than inventing a rating.

### Enable the workflow

1. Push the whole project, including `.github/workflows/update-ratings.yml`, `scripts/update_ratings.py`, and `data/ratings.json`.
2. In GitHub, open **Settings → Actions → General** and allow workflows read/write repository contents if that option is restricted.
3. Open **Actions → Update competitive programming ratings → Run workflow** for the first update.
4. Inspect `data/ratings.json` after the run. The workflow commits changed snapshots automatically.
5. Ensure GitHub Pages publishes from the branch/root containing `index.html` and `data/ratings.json`.

Scheduled snapshots run approximately every six hours; GitHub may delay scheduled jobs during high load. They are not instant in-contest rating estimates.

File roles: `index.html` is page structure, `css/style.css` is styling, `js/script.js` loads the snapshot and handles the mobile menu, and `scripts/update_ratings.py` fetches rating data.
