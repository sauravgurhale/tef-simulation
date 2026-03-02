# EXTRACT_CE_HTML_PROMPT

Use this exact prompt in Openclaw.

```text
You are extracting CE (Comprehension Ecrite) practice HTML from my already-authenticated tefcanada.ca session in Firefox.

Goal
- Extract the full HTML source for all 19 CE practices (the page that shows questions, answer options, and the correct answers/explanations).
- Save each extracted HTML file into my local git repository with the exact path and naming convention below.

Environment
- Browser: Firefox (already logged in to tefcanada.ca).
- Repository root (absolute path): /Users/saurav.gurhale/Desktop/github/tef-simulation

CE practices to extract
1. CE Practice 1  -> ce_web_content/ce_1/ce_1.html
2. CE Practice 2  -> ce_web_content/ce_2/ce_2.html
3. CE Practice 3  -> ce_web_content/ce_3/ce_3.html
4. CE Practice 4  -> ce_web_content/ce_4/ce_4.html
5. CE Practice 5  -> ce_web_content/ce_5/ce_5.html
6. CE Practice 6  -> ce_web_content/ce_6/ce_6.html
7. CE Practice 7  -> ce_web_content/ce_7/ce_7.html
8. CE Practice 8  -> ce_web_content/ce_8/ce_8.html
9. CE Practice 9  -> ce_web_content/ce_9/ce_9.html
10. CE Practice 10 -> ce_web_content/ce_10/ce_10.html
11. CE Practice 11 -> ce_web_content/ce_11/ce_11.html
12. CE Practice 12 -> ce_web_content/ce_12/ce_12.html
13. CE Practice 13 -> ce_web_content/ce_13/ce_13.html
14. CE Practice 14 -> ce_web_content/ce_14/ce_14.html
15. CE Practice 15 -> ce_web_content/ce_15/ce_15.html
16. CE Practice 16 -> ce_web_content/ce_16/ce_16.html
17. CE Practice 17 -> ce_web_content/ce_17/ce_17.html
18. CE Practice 18 -> ce_web_content/ce_18/ce_18.html
19. CE Practice 19 -> ce_web_content/ce_19/ce_19.html

What to do for each practice
1. Go to the CE practice entry page/list on tefcanada.ca.
2. Open the target practice number.
3. Navigate to the page/view that contains:
   - all questions,
   - all answer options,
   - and the correct answers/explanations (if shown behind a correction/result view, open that view first).
4. Extract the complete HTML document from that page:
   - Prefer "View Page Source" and save the full HTML,
   - or capture document.documentElement.outerHTML if source view is unavailable.
5. Save to the exact destination file in the repo (overwrite existing file).

Repository structure and naming rules (must follow exactly)
- Base folder: ce_web_content/
- One folder per CE practice: ce_<n>
- HTML filename inside each folder: ce_<n>.html
- Example: ce_web_content/ce_1/ce_1.html
- Use only these exact paths; do not create alternate filenames.

Validation after extraction
- Confirm all 19 files exist at:
  - ce_web_content/ce_1/ce_1.html ... ce_web_content/ce_19/ce_19.html
- Confirm each file is non-empty and contains HTML markup.
- Output a final checklist with 19 lines: practice number, saved path, status (OK/FAILED).

Important constraints
- Do not log out of tefcanada.ca.
- Do not modify JSON files in this step.
- Do not save to Downloads; save directly into the repository paths above.
```
