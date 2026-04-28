import { expect, test } from "@playwright/test";

test.describe("Smoke — frontend loads", () => {
  test("homepage renders with navigation", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/weather|meteo|analyzer/i);

    // Main navigation visible
    await expect(
      page.getByRole("link", { name: /egyetlen város/i }).or(
        page.getByRole("link", { name: /single.city/i }),
      ),
    ).toBeVisible({ timeout: 10_000 });
  });
});

test.describe("Smoke — city search API proxy", () => {
  test("city search returns results via /api proxy", async ({ page }) => {
    // Navigate first so the proxy is active
    await page.goto("/");

    const response = await page.request.get(
      "/api/cities/search?query=Budapest&limit=5",
    );
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body.cities).toBeDefined();
    expect(body.cities.length).toBeGreaterThan(0);
    expect(body.cities[0].name).toContain("Budapest");
  });
});

test.describe("Smoke — health endpoints", () => {
  test("backend /health is reachable through proxy", async ({ page }) => {
    await page.goto("/");

    const response = await page.request.get("/health");
    expect(response.ok()).toBeTruthy();
  });

  test("metadata /api/weather/metrics returns data", async ({ page }) => {
    await page.goto("/");

    const response = await page.request.get("/api/weather/metrics");
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body.metrics).toBeDefined();
    expect(Object.keys(body.metrics).length).toBeGreaterThan(0);
  });
});
