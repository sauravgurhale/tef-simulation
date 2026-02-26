import argparse
import json
import os
import re
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests


class QuestionDOMParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.questions: Dict[str, Dict[str, object]] = {}
        self._in_question = False
        self._question_div_depth = 0
        self._current_question_id: Optional[str] = None
        self._current_options: List[Tuple[str, List[str]]] = []
        self._current_transcript_parts: List[str] = []
        self._current_correct_index: Optional[int] = None
        self._option_index = 0

        self._in_option_label = False
        self._in_option_item = False
        self._option_is_correct = False
        self._current_option_text_parts: List[str] = []
        self._current_option_img_urls: List[str] = []

        self._in_explanation = False
        self._explanation_div_depth = 0
        self._in_strong = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attrs_dict = {key: value for key, value in attrs}
        class_attr = attrs_dict.get("class", "") or ""

        if tag == "div":
            if (
                not self._in_question
                and "question" in class_attr.split()
                and "data-id" in attrs_dict
            ):
                self._in_question = True
                self._question_div_depth = 1
                self._current_question_id = attrs_dict.get("data-id")
                self._current_options = []
                self._current_transcript_parts = []
                self._current_correct_index = None
                self._option_index = 0
                return

            if self._in_question:
                self._question_div_depth += 1

                if "question-explanation-content" in class_attr:
                    self._in_explanation = True
                    self._explanation_div_depth = 1
                elif self._in_explanation:
                    self._explanation_div_depth += 1

        if tag == "label" and "option-title" in class_attr.split():
            self._in_option_label = True
            self._current_option_text_parts = []
            self._current_option_img_urls = []

        if tag == "li" and "answer-option" in class_attr:
            self._in_option_item = True
            self._option_is_correct = "answer-correct" in class_attr.split()

        if self._in_option_label and tag == "img":
            src = attrs_dict.get("src")
            if src:
                self._current_option_img_urls.append(src)

        if self._in_explanation and tag == "strong":
            self._in_strong = True

    def handle_data(self, data: str) -> None:
        if self._in_option_label:
            self._current_option_text_parts.append(data)
            return

        if self._in_explanation and not self._in_strong:
            self._current_transcript_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self._in_option_label:
            text = normalize_whitespace("".join(self._current_option_text_parts))
            self._current_options.append((text, self._current_option_img_urls))
            if self._in_option_item:
                if self._option_is_correct:
                    self._current_correct_index = self._option_index
                self._option_index += 1
            self._in_option_label = False
            self._current_option_text_parts = []
            self._current_option_img_urls = []
            return

        if tag == "li" and self._in_option_item:
            self._in_option_item = False
            self._option_is_correct = False

        if tag == "strong" and self._in_strong:
            self._in_strong = False
            return

        if tag == "div" and self._in_question:
            self._question_div_depth -= 1

            if self._in_explanation:
                self._explanation_div_depth -= 1
                if self._explanation_div_depth <= 0:
                    self._in_explanation = False
                    self._explanation_div_depth = 0

            if self._question_div_depth <= 0:
                transcript = normalize_whitespace(
                    "".join(self._current_transcript_parts)
                )
                transcript = re.sub(
                    r"^Transcription\s*-\s*", "", transcript, flags=re.IGNORECASE
                )
                if self._current_question_id:
                    self.questions[self._current_question_id] = {
                        "options": self._current_options,
                        "transcript": transcript,
                        "correct_index": self._current_correct_index,
                    }
                self._in_question = False
                self._current_question_id = None
                self._current_options = []
                self._current_transcript_parts = []


class SimpleHTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text_parts: List[str] = []
        self.image_urls: List[str] = []
        self._skip_content = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attrs_dict = {key: value for key, value in attrs}

        if tag == "img":
            src = attrs_dict.get("src")
            if src:
                self.image_urls.append(src)

        if tag == "iframe":
            self._skip_content = True

        if tag == "br":
            self.text_parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag == "iframe":
            self._skip_content = False

    def handle_data(self, data: str) -> None:
        if self._skip_content:
            return
        self.text_parts.append(data)


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def extract_js_object(html: str, marker: str) -> str:
    marker_index = html.find(marker)
    if marker_index == -1:
        raise ValueError(f"Marker not found: {marker}")

    start_index = html.find("{", marker_index)
    if start_index == -1:
        raise ValueError("JSON object start not found")

    depth = 0
    in_string = False
    escape = False
    for i in range(start_index, len(html)):
        char = html[i]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return html[start_index: i + 1]

    raise ValueError("JSON object end not found")


def extract_text_and_images(html_fragment: str) -> Tuple[str, List[str]]:
    parser = SimpleHTMLTextParser()
    parser.feed(html_fragment)
    text = normalize_whitespace("".join(parser.text_parts))
    return text, parser.image_urls


def safe_filename(url: str, fallback_index: int) -> str:
    parsed = urlparse(url)
    basename = os.path.basename(parsed.path)
    if basename:
        return basename
    return f"image_{fallback_index}.bin"


def download_images(image_urls: List[str], output_dir: str) -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    url_to_path: Dict[str, str] = {}
    used_names: Dict[str, int] = {}

    for index, url in enumerate(image_urls, start=1):
        filename = safe_filename(url, index)
        base, ext = os.path.splitext(filename)
        if not ext:
            ext = ".bin"

        dedup_name = filename
        if dedup_name in used_names:
            used_names[dedup_name] += 1
            dedup_name = f"{base}_{used_names[dedup_name]}{ext}"
        else:
            used_names[dedup_name] = 1

        output_path = os.path.join(output_dir, dedup_name)
        if not os.path.exists(output_path):
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(output_path, "wb") as file_handle:
                file_handle.write(response.content)

        url_to_path[url] = output_path

    return url_to_path


def safe_dom_options(dom_data: object) -> List[Tuple[str, List[str]]]:
    if not isinstance(dom_data, dict):
        return []
    options = dom_data.get("options")
    if isinstance(options, list):
        return options
    return []


def safe_dom_transcript(dom_data: object) -> str:
    if not isinstance(dom_data, dict):
        return ""
    transcript = dom_data.get("transcript")
    if isinstance(transcript, str):
        return transcript
    return ""


def safe_dom_correct_index(dom_data: object) -> Optional[int]:
    if not isinstance(dom_data, dict):
        return None
    correct_index = dom_data.get("correct_index")
    if isinstance(correct_index, int):
        return correct_index
    return None


def build_output(
    html_path: str,
    output_json_path: str,
    images_dir: str,
) -> None:
    with open(html_path, "r", encoding="utf-8") as file_handle:
        html_content = file_handle.read()

    quiz_json_text = extract_js_object(html_content, "var lp_quiz_js_data")
    quiz_data = json.loads(quiz_json_text)
    questions_data = quiz_data.get("data", {}).get("questions", [])

    dom_parser = QuestionDOMParser()
    dom_parser.feed(html_content)

    image_urls: List[str] = []
    question_media: Dict[str, List[str]] = {}

    for question in questions_data:
        question_id = str(question.get("id"))
        title_html = question.get("title", "")
        _, images = extract_text_and_images(title_html)
        question_media[question_id] = images
        image_urls.extend(images)

    for question_id, dom_data in dom_parser.questions.items():
        for _, img_urls in safe_dom_options(dom_data):
            image_urls.extend(img_urls)

    unique_image_urls = sorted(set(image_urls))
    url_to_local_path = download_images(unique_image_urls, images_dir)

    output_questions: List[Dict[str, object]] = []
    for index, question in enumerate(questions_data, start=1):
        question_id = str(question.get("id"))
        title_html = question.get("title", "")
        question_text, _ = extract_text_and_images(title_html)

        local_images = [
            url_to_local_path[url]
            for url in question_media.get(question_id, [])
            if url in url_to_local_path
        ]
        if local_images:
            question_text = (
                question_text
                + "\n"
                + "\n".join([f"[image] {path}" for path in local_images])
            )

        dom_data = dom_parser.questions.get(question_id, {})
        options: List[str] = []
        for option_text, img_urls in safe_dom_options(dom_data):
            if option_text:
                options.append(option_text)
            elif img_urls:
                img_url = img_urls[0]
                if img_url:
                    options.append(url_to_local_path.get(img_url, img_url))
                else:
                    options.append("")
            else:
                options.append("")

        transcript = safe_dom_transcript(dom_data)
        correct_index = safe_dom_correct_index(dom_data)
        right_option = ""
        if correct_index is not None and 0 <= correct_index < 4:
            right_option = ["A", "B", "C", "D"][correct_index]

        output_questions.append(
            {
                "question_no": index,
                "question": question_text,
                "options": options,
                "audio_transcript": transcript,
                "right_option": right_option,
            }
        )

    if len(output_questions) != 40:
        raise ValueError(f"Expected 40 questions, found {len(output_questions)}")

    for question in output_questions:
        options_list = question.get("options")
        if not isinstance(options_list, list) or len(options_list) != 4:
            options_len = len(options_list) if isinstance(options_list, list) else 0
            raise ValueError(
                f"Question {question.get('question_no')} has {options_len} options"
            )

    with open(output_json_path, "w", encoding="utf-8") as file_handle:
        json.dump(output_questions, file_handle, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract CO quiz data from HTML")
    parser.add_argument(
        "--html",
        default="co_web_content/co_18.html",
        help="Path to the source HTML file",
    )
    parser.add_argument(
        "--out-json",
        default="co_web_content/co_18.json",
        help="Path to the output JSON file",
    )
    parser.add_argument(
        "--images-dir",
        default="co_web_content/co_18_images",
        help="Directory to store downloaded images",
    )

    args = parser.parse_args()
    build_output(args.html, args.out_json, args.images_dir)


if __name__ == "__main__":
    main()
