# Boutique Manager - App

React + Ionic frontend, talks to the cloud API in `../backend`. Same
codebase produces three things: a website, an installable PWA (Add to
Home Screen, no app store), and native Android/iOS apps via Capacitor.

## 1. Local development

```
npm install
cp .env.example .env.local        # then edit VITE_API_URL if needed
npm run dev
```

By default it points at `http://localhost:8000` - run the backend
alongside it (see `../backend/README.md`) for a fully working local setup.
Once the backend is deployed on Railway, set `VITE_API_URL` in `.env.local`
to that live URL instead.

## 2. Fastest way onto a device: PWA (no app store, no waiting)

This is already wired up (`vite-plugin-pwa`) - once deployed to any static
host, anyone can visit the site on their phone and use their browser's
"Add to Home Screen" (Android Chrome) or "Add to Home Screen" from the
Share menu (iPhone Safari). It then behaves like an installed app - own
icon, opens full-screen, works after a restart - with zero app-store
review and no cost.

To deploy:
```
npm run build
```
This produces a `dist/` folder - drag-and-drop it onto **Netlify Drop**
(app.netlify.com/drop) for the fastest possible live URL, or connect the
repo to **Vercel** or **Netlify** properly for auto-deploys on every push.
Either is free for a project this size.

**Do this first** - it gets the app onto your and your friends' phones
today, while the store submissions below happen in parallel (they can
take days for review).

## 3. Android app (.apk / Play Store)

Requires **Android Studio** installed on your PC (free, from
developer.android.com/studio) - it bundles the Android SDK and Gradle,
neither of which can be installed in a plain terminal without it.

```
npm run build
npx cap sync android
npx cap open android
```

That last command opens the project in Android Studio. From there:
- **Quick sideload (no Play Store)**: Build -> Build Bundle(s)/APK(s) ->
  Build APK(s). The resulting `.apk` in `android/app/build/outputs/apk/debug/`
  can be sent directly to a friend's phone (they'll need to allow
  "install from unknown sources" once) - no Play Store account needed.
- **Play Store release**: Build -> Generate Signed Bundle/APK -> follow the
  signing wizard (creates a keystore - keep this file safe, you'll need
  the same one for every future update). Upload the resulting `.aab` to
  Google Play Console (developer.android.com/console, $25 one-time) under
  a new app listing.

## 4. iOS app (.ipa / App Store)

Requires a **Mac** with **Xcode** installed - this cannot be built from
Windows or Linux; Apple only allows building/signing iOS apps on macOS.

```
npm run build
npx cap sync ios
npx cap open ios
```

Opens the project in Xcode. From there: Product -> Archive, then use the
Organizer window to either export a `.ipa` for direct device testing
(via Xcode or TestFlight) or submit to App Store Connect. Requires an
Apple Developer account ($99/year) to distribute beyond your own devices.

If you don't have access to a Mac, services like Ionic Appflow or
Codemagic can build iOS apps in the cloud from this same repo - worth
looking into if this becomes a real blocker later.

## 5. After any code change

Whenever you update the React code and want the native apps to reflect
it:
```
npm run build
npx cap sync
```
Then rebuild in Android Studio / Xcode as above. The web/PWA deploy
(step 2) just needs a fresh `npm run build` + redeploy - no separate sync
step for that one.

## Design

Custom visual identity in `src/theme/` (`variables.css` for the color
system, `global.css` for typography and the signature motif) - not
Ionic's default blue. Palette is grounded in the actual product: deep
aubergine (fabric-dye), antique gold (embroidery thread), warm ivory
(unbleached cotton). Fraunces (a warm serif) for titles and dashboard
figures, Manrope for everything functional. The recurring signature is a
dashed gold "stitch line" - referencing hand-stitched fabric edges - used
as a consistent top border on cards and section dividers throughout.

I verified this compiles and bundles correctly (`npm run build` succeeds
cleanly), but couldn't render and screenshot it myself - Playwright's
browser download is blocked by this environment's network allowlist
(`cdn.playwright.dev` isn't reachable). Worth an actual look with
`npm run dev` before you consider it final; I'm confident in the CSS
mechanics (Ionic's shadow-DOM component theming needs its specific
`--custom-property` pattern, which this uses correctly) but not in the
final visual balance the way a screenshot would confirm.

## What's built

Login/signup (with lockout after repeated failed attempts), Dashboard
(today/month totals, low stock, inventory value), Inventory (search, add
stock, duplicate-detection prompt, tap any product to edit details or
upload/change its photo, remove from inventory), Sell Product (search,
record sale, recent transactions, full refund dialog with quantity +
reason), Customers, Suppliers, Settings (shop info, logout).

## Known gaps

- No offline support - unlike the original desktop app, this version
  needs an internet connection to load/save anything, since data now
  lives on the server, not on the device. Fixing this properly means
  local caching + a sync queue for offline writes - a real feature, not
  a quick add, so it's deliberately left for later rather than half-built.
- No email verification on signup (backend gap, see `../backend/README.md`)
  - anyone can sign up with any email without proving they own it.
