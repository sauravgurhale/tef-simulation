# EXTRACT_CE_HTML_PROMPT

Use this exact prompt in Openclaw.

```text
You are extracting CE (Comprehension Ecrite) practice HTML from my already-authenticated tefcanada.ca session in Firefox.

Goal
- Extract the full HTML source for all 19 CE practices (the page that shows questions, answer options, and the correct answers/explanations).
- Save each extracted HTML file into my local git repository with the exact path and naming convention below.
- Also save one question image from each practice into that practice's `assets` folder.

Environment
- Browser: Firefox (already logged in to tefcanada.ca).
- Repository root (absolute path): /Users/saurav.gurhale/Desktop/github/tef-simulation

Direct quiz links and target save paths
1. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-1-3/  -> ce_web_content/ce_1/ce_1.html
2. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-2/    -> ce_web_content/ce_2/ce_2.html
3. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-3/    -> ce_web_content/ce_3/ce_3.html
4. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-4/    -> ce_web_content/ce_4/ce_4.html
5. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-5/    -> ce_web_content/ce_5/ce_5.html
6. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-6/    -> ce_web_content/ce_6/ce_6.html
7. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-7/    -> ce_web_content/ce_7/ce_7.html
8. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-8/    -> ce_web_content/ce_8/ce_8.html
9. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-9/    -> ce_web_content/ce_9/ce_9.html
10. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-10/  -> ce_web_content/ce_10/ce_10.html
11. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-11/  -> ce_web_content/ce_11/ce_11.html
12. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-12/  -> ce_web_content/ce_12/ce_12.html
13. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-13/  -> ce_web_content/ce_13/ce_13.html
14. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-14/  -> ce_web_content/ce_14/ce_14.html
15. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-15/  -> ce_web_content/ce_15/ce_15.html
16. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-16/  -> ce_web_content/ce_16/ce_16.html
17. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-17/  -> ce_web_content/ce_17/ce_17.html
18. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-18/  -> ce_web_content/ce_18/ce_18.html
19. https://tefcanada.ca/courses/tef-canada-preparation-premium-plan/quizzes/ce-mock-exam-19/  -> ce_web_content/ce_19/ce_19.html

What to do for each practice
1. Open the exact quiz URL for that practice.
2. Navigate to the page/view that contains:
   - all questions,
   - all answer options,
   - and the correct answers/explanations (if shown behind a correction/result view, open that view first).
3. Extract the complete HTML document from that page:
   - Prefer "View Page Source" and save the full HTML,
   - or capture document.documentElement.outerHTML if source view is unavailable.
4. Save to the exact destination file in the repo (overwrite existing file).
5. Save one representative question image from that same practice:
   - Pick any one image used by a question/passage.
   - Save it as: ce_web_content/ce_<n>/assets/ce-<n>-1-min.png
   - Example for practice 7: ce_web_content/ce_7/assets/ce-7-1-min.png

Repository structure and naming rules (must follow exactly)
- Base folder: ce_web_content/
- One folder per CE practice: ce_<n>
- HTML filename inside each folder: ce_<n>.html
- Asset subfolder inside each practice: assets/
- One extracted image filename: ce-<n>-1-min.png
- Example: ce_web_content/ce_1/ce_1.html
- Example image: ce_web_content/ce_1/assets/ce-1-1-min.png
- Use only these exact paths; do not create alternate filenames.

Validation after extraction
- Confirm all 19 files exist at:
  - ce_web_content/ce_1/ce_1.html ... ce_web_content/ce_19/ce_19.html
- Confirm all 19 image files exist at:
  - ce_web_content/ce_1/assets/ce-1-1-min.png ... ce_web_content/ce_19/assets/ce-19-1-min.png
- Confirm each file is non-empty and contains HTML markup.
- Confirm each saved image file is non-empty.
- Output a final checklist with 19 lines: practice number, URL used, html path, image path, status (OK/FAILED).

Important constraints
- Do not log out of tefcanada.ca.
- Do not modify JSON files in this step.
- Do not save to Downloads; save directly into the repository paths above.
```
