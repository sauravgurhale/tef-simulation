# Reusable Prompt: Segment a TEF CO Raw Audio File into 44 Final Segments

Use this prompt to invoke Claude Code to process a new raw audio file.
Replace the bracketed placeholders before running.

---

## Prompt (copy-paste this)

```
I need to segment a raw TEF CO audio file into exactly 44 final segments
(segment_01.mp3 through segment_44.mp3) for practice_[N].

## Paths
- Raw audio:       co_web_content/practice_[N]/audio/full_raw/co_[N]_full_raw.mp3
- Final output:    co_web_content/practice_[N]/audio/
- Raw work dir:    /tmp/co_[N]_raw/
- Scripts:         api/src/
- Project venv:    /Users/saurav.gurhale/Desktop/github/tef-simulation/venv

## Target layout (44 segments)
seg_01       → Group 1 intro
seg_02–05    → Q1–Q4   (Group 1)
seg_06       → Group 2 intro
seg_07–10    → Q5–Q8   (Group 2)
seg_11       → Group 3 intro
seg_12–17    → Q9–Q14  (Group 3)
seg_18       → Group 4 intro
seg_19–21    → Q15–Q17 (Group 4)
seg_22       → Group 5 intro
seg_23–25    → Q18–Q20 (Group 5)
seg_26       → Group 6 intro
seg_27–28    → Q21–Q22 (Group 6)
seg_29       → Group 7 intro  (Reportage Radio – "répondez à deux questions")
seg_30–33    → Dialogue pairs (Q23–Q30, 2 questions per segment)
seg_34       → Group 8 intro
seg_35–44    → Q31–Q40 (Group 8)

## Steps to follow

### Step 1 – Segment
Run segment_local_audio.py with the project venv:
  source venv/bin/activate
  cd api/src
  python segment_local_audio.py \
    --input ../../co_web_content/practice_[N]/audio/full_raw/co_[N]_full_raw.mp3 \
    --output /tmp/co_[N]_raw

Print the full index/duration table so I can see all raw segments.

### Step 2 – Analyze
Run analyze_segments.py:
  python analyze_segments.py --input /tmp/co_[N]_raw

Show me the full analysis report (durations, SHORT/LONG flags, duplicate pairs).

### Step 3 – Draft segment_map.json
Based on the analysis and the target layout above, draft /tmp/co_[N]_raw/segment_map.json.

Rules for the draft:
- The total raw segments will likely be 46 (need to drop 2 to reach 44).
- Common drops:
    • Any segment < 2s (silence artifact)
    • A repeated group intro (same "répondez à..." phrase appearing twice)
- Group intros are short (5–15s); question audio is longer (15–160s).
- Group 7 "Reportage Radio" intro is distinctively short (~7–8s).
- Dialogue pairs (seg_30–33) can be long (50–160s each – full radio report).
- Group 8 intro is short (5–10s), followed by 10 question segments.
- If a group intro appears twice in the raw audio, use the FIRST occurrence
  and drop the SECOND (the repeat appears after the content it introduced).
- sources with >1 file = combine them using combine_audio_files.py.
- "drop" list is informational only.

Clearly mark any uncertain assignments with "?? — verify by listening".

### Step 4 – Open for review
Open /tmp/co_[N]_raw/ in Finder so I can listen.
Present a summary table of the draft mapping and flag:
  - Any segment I should listen to before confirming
  - The two proposed drops and why

Wait for me to confirm or correct the mapping.

### Optional: Correlate transcripts to segment durations
If a co_N.json exists at co_web_content/practice_N/co_N.json, use it to
cross-check the mapping. Each question entry has an "audio_transcript" field.
Longer transcripts → longer audio segments. Use this to:
  - Confirm that a flagged LONG segment (e.g. 120s) really is a long question
    (check its transcript length vs. surrounding questions)
  - Identify which raw segment corresponds to which question number when
    the duration alone is ambiguous
  - Detect mismatches: if raw_037 (30s) maps to a question whose transcript
    is 10x longer than the surrounding questions, something is wrong
The JSON has exactly 40 entries (Q1–Q40). Group intros are NOT in the JSON.
Segment layout reminder: seg_02–05=Q1–4, seg_07–10=Q5–8, seg_12–17=Q9–14,
seg_19–21=Q15–17, seg_23–25=Q18–20, seg_27–28=Q21–22, seg_30–33=Q23–30
(pairs), seg_35–44=Q31–40.

### Step 5 – Finalize
Once I confirm the map, run finalize_segments.py:
  python finalize_segments.py \
    --map /tmp/co_[N]_raw/segment_map.json \
    --output ../../co_web_content/practice_[N]/audio

Then verify:
  ls co_web_content/practice_[N]/audio/segment_*.mp3 | wc -l   → must print 44
  ls co_web_content/practice_[N]/audio/segment_*.mp3            → segment_01 … segment_44
```

---

## Notes from Practice 2 (reference)

- 48 raw segments produced. Needed 4 drops to reach 44.
- `analyze_segments.py` caught **3 near-perfect duplicate pairs** (sim ~0.999): raw_030/031, raw_032/033, raw_034/035. Keep the first of each pair.
- raw_036 (9.4s) = repeated Group 7 "Reportage Radio" intro mid-dialogue → drop.
- raw_037 (122.8s) = Dialogue pair 4 (full radio report, Q29-30) → seg_33 ✓
- raw_038 (9.0s) = Group 8 intro ("documents divers") → seg_34 ✓
- Group 8 intro phrase: **"Introduction: documents divers"** (differs from Group 7 which says "Reportage Radio, répondez à deux questions").

## Notes from Practice 1 (reference)

- 46 raw segments were produced with default silence params (min_silence=3500ms).
- Drops: `raw_030` (1042ms artifact) + `raw_034` (repeated Group 7 intro).
- raw_029 = first Group 7 intro → seg_29 ✓
- raw_034 = repeated Group 7 intro → dropped ✓
- raw_035 (153s) = Dialogue pair 4 (full radio report, long but correct) → seg_33 ✓
- raw_036 (6.5s) = Group 8 intro → seg_34 ✓
- Segment map saved at: `/tmp/co_1_raw/segment_map.json`

## Scripts location

| Script                   | Purpose                                      |
|--------------------------|----------------------------------------------|
| `api/src/segment_local_audio.py`  | Silence-based segmenter (no Supabase) |
| `api/src/analyze_segments.py`     | Duration table + duplicate detection  |
| `api/src/finalize_segments.py`    | Applies segment_map.json → 44 files   |
| `api/src/combine_audio_files.py`  | Concatenates MP3s (used by finalize)  |
