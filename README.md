# apexfitnesscentre.shop

The website builds and publishes itself. **You never upload the site by hand again.**

- `source/` – everything you edit (blog posts, products, photos, design)
- everything else at the top of this repo is the finished website, rebuilt automatically. Don't edit those files; your changes would be overwritten.

## Write a blog post (works on your phone)

1. Open **source/content/blog/_TEMPLATE.md** and copy all of it.
2. Go back to **source/content/blog**, tap **Add file → Create new file**.
3. Name it `2026-11-02-your-post-name.md` (date, then the web address you want, with dashes).
4. Paste the template, change the lines at the top, write your post under the second `---`.
5. Make sure it says `draft: false` (or delete the draft line). Tap **Commit changes**.

About 2 minutes later it is live at `apexfitnesscentre.shop/blog/your-post-name/`, and it is added to the blog page, the sitemap and the RSS feed automatically.

- **Photos:** upload to `source/content/blog/images/` first (Add file → Upload files), then use `image: photo.jpg` at the top or `![description](images/photo.jpg)` in the text. Big phone photos are shrunk automatically.
- **Schedule a post:** give it a future date. It goes live by itself that morning (around 6 AM Nepal time).
- **Fix a typo:** open the post, tap the pencil, edit, Commit. Live in 2 minutes.
- **Something wrong?** If a post has a mistake at the top (missing title, wrong date format), the website simply does not change and GitHub emails you. Open the **Actions** tab, tap the red ❌ run, and the last lines say which file and what is wrong.

## Other everyday changes

| What | Where |
|---|---|
| Product price, name, text | `source/build.py` (first products) and `source/newprods.py` |
| Out of stock | `STOCK = {...}` near the top of `source/build.py` |
| Google Analytics ID | `GA_ID` near the top of `source/build.py` (tracking stays off until a real ID is set) |
| Google AdSense ID | `ADSENSE_CLIENT` near the top of `source/build.py` (also creates ads.txt) |
| Which pages show ads | `ADS_ON` in `source/build.py` (blog, guides, calculators only; shop pages stay ad-free) |
| Google Search Console verification | `GSC_VERIFY` in `source/build.py` (paste only the content="..." value) |
| Customer reviews | `REVIEWS` in `source/build.py`, photos in `source/assets/reviews/` |
| Colours and design | `source/premium.css` |

## Rebuild by hand

**Actions** tab → **Build and publish the website** → **Run workflow**.
