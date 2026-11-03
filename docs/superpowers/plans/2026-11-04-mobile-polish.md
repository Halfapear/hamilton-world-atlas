# Mobile Polish Implementation Plan

> Inline execution: use executing-plans and verify each task. User requests editing the existing checkout, not a new worktree.

**Goal:** Deliver the approved mobile-first Hamilton interface, tested upload ZIP and user-operated note publishing instructions; continue official support/upload inquiry without publishing a note.

**Architecture:** Add shared local CSS and a shared quick-start renderer to the web template and sandbox app. Keep their existing storage/link behavior. Embed CSS in HTML at build time; render quick entry times from DATA, not a separate ticket-data copy.

**Tech Stack:** HTML/CSS/JavaScript, Python build and Playwright, Windows UI Automation for verified existing browser windows.

## Task 1: Red tests

- [x] Add mobile checks to tests/test_app.py and ../小红书版/tests/test_minitool.py: hero height <=260, quick area visible, map top <780, controls >=44, Korea buttons target correct detail.
- [x] Run both against current pages; record expected failures before UI implementation.

## Task 2: Shared UI

- [x] Create src/mobile-polish.css: narrow hero, 44px controls, quick section; mini container top offset 56px.
- [x] Create src/quick-start.js: function renderQuickStart() reading DATA stops/meta and inserting buttons into #korea-quick-start.
- [x] Insert the quick-section container below home hero in both HTML sources; call renderer at startup. Embed shared CSS/JS into web template/build output and equivalent local mini files, without inline mini scripts.
- [x] Run python tools/build.py, node --check MiniTool/app.js and both browser suites; fix only errors proven by output. Final web95 and mini24 checks in each browser; geometry2 and independent-build1.

## Task 3: Artifacts and delivery

- [x] Save desktop/mobile and Korea quick-entry screenshots; inspect rendered images for clipping/overflow.
- [x] Update manual publishing guide with account/approval/activity conditions; preserve original activity share text and avoid fake eligibility claims.
- [x] Package a new named upload ZIP with index.html at root; inspect entries; do not overwrite earlier packages.
- [ ] Commit scoped web and mini-source changes to existing Hamilton repository, push non-force and verify remote commit.

## Task 4: External gates

- [ ] Inspect live 360 browser and verify nickname/account before any upload.
- [ ] Read official activity rules and choose official participation flow only if eligible; do not equate a hashtag with participation.
- [x] Check support response/entry; report exact limitations requiring user authentication, without changing identity binding.
- [x] Prepare user-operated instructions; do not click Publish.

External evidence: 360 visible but no accessible document and safe focus failed; nickname/upload unresolved. Edge activity center page2 lists 小工具作品激励开启, 11-01–12-31, #小红书小工具, 去发布. Full eligibility and cross-account mounting not displayed. Support has no human answer or receipt. No note published, no identity unlinked.
