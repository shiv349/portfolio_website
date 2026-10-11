const toggle = document.getElementById("menuToggle");
const links = document.getElementById("navLinks");

if (toggle && links) {
    toggle.addEventListener("click", () => {
        const open = links.classList.toggle("open");
        toggle.setAttribute("aria-expanded", String(open));
    });
    links.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            links.classList.remove("open");
            toggle.setAttribute("aria-expanded", "false");
        });
    });
}

const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();

const PLATFORMS = ["leetcode", "codeforces", "codechef"];
function formatRating(value) {
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0) return "Unavailable";
    return Math.round(value).toLocaleString();
}
function showRating(platform, data, fallback = false) {
    const current = document.getElementById(`${platform}-current`);
    const highest = document.getElementById(`${platform}-highest`);
    const status = document.getElementById(`${platform}-status`);
    if (!current || !highest || !status) return;
    current.textContent = formatRating(data?.current);
    highest.textContent = formatRating(data?.highest);
    const hasValue = typeof data?.current === "number" || typeof data?.highest === "number";
    status.classList.toggle("is-live", !fallback && data?.status === "ok" && hasValue);
    status.classList.toggle("is-fallback", fallback || data?.status !== "ok" || !hasValue);
    status.textContent = data?.status === "ok" && hasValue ? "Updated" : hasValue ? "Last saved" : "Unavailable";
}
async function loadRatings() {
    const updated = document.getElementById("ratingsUpdated");
    try {
        const response = await fetch("data/ratings.json", { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        const ratings = payload?.ratings || {};
        PLATFORMS.forEach((platform) => showRating(platform, ratings[platform], ratings[platform]?.status !== "ok"));
        if (updated) {
            const date = payload?.updatedAt ? new Date(payload.updatedAt) : null;
            updated.textContent = date && !Number.isNaN(date.getTime())
                ? `Last refresh attempt: ${date.toLocaleString()}. Ratings are scheduled snapshots, not instant in-contest estimates.`
                : "Showing the latest saved snapshot. Ratings update on a schedule, not instantly.";
        }
    } catch (error) {
        console.error("Could not load ratings:", error);
        PLATFORMS.forEach((platform) => showRating(platform, null, true));
        if (updated) updated.textContent = "Rating data could not be loaded. Please try again later or visit the profile links.";
    }
}
loadRatings();
