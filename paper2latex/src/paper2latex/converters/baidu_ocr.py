"""
百度智能云OCR实现
"""

import logging
import requests
import base64
import fitz
import time

logger = logging.getLogger(__name__)


class BaiduOCR:
    """百度智能云OCR"""

    def __init__(self, config):
        self.api_key = config.paddle_access_token
        self.secret_key = config.paddle_secret_key
        self.access_token = None
        self.qps = max(float(getattr(config, "baidu_ocr_qps", 2.0)), 0.1)
        self.max_retries = max(int(getattr(config, "baidu_ocr_max_retries", 6)), 1)
        self.retry_backoff_sec = max(float(getattr(config, "baidu_ocr_retry_backoff_sec", 1.0)), 0.2)
        self._min_interval_sec = 1.0 / self.qps
        self._last_request_ts = 0.0
        logger.info("Initialized Baidu Cloud OCR")

    def _get_access_token(self):
        """获取access token"""
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        response = requests.post(url)
        return response.json().get("access_token")

    def _throttle(self):
        """严格限流，保证请求速率不超过配置QPS。"""
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        if elapsed < self._min_interval_sec:
            time.sleep(self._min_interval_sec - elapsed)
        self._last_request_ts = time.monotonic()

    def _request_page_with_retry(self, url: str, payload: dict, page_num: int) -> dict:
        """请求单页OCR并处理QPS超限重试。"""
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            response = requests.post(url, data=payload, timeout=60)
            result = response.json()

            error_code = result.get("error_code")
            if error_code in {18, 19}:  # 18: QPS超限; 19: 总并发超限
                sleep_sec = self.retry_backoff_sec * attempt
                logger.warning(
                    "Baidu OCR rate limited on page %s (error_code=%s), retry %s/%s after %.1fs",
                    page_num + 1,
                    error_code,
                    attempt,
                    self.max_retries,
                    sleep_sec,
                )
                time.sleep(sleep_sec)
                continue

            return result

        raise RuntimeError(
            f"Baidu OCR rate limit persisted after {self.max_retries} retries on page {page_num + 1}"
        )

    def convert(self, pdf_path: str, output_mode: str = "simple") -> str:
        """调用百度OCR"""
        if not self.access_token:
            self.access_token = self._get_access_token()

        doc = fitz.open(pdf_path)
        results = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=150)
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode()

            url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={self.access_token}"
            result = self._request_page_with_retry(
                url=url,
                payload={"image": img_base64},
                page_num=page_num,
            )

            if result.get("error_code") == 17:
                raise RuntimeError("Baidu OCR daily request limit reached (error_code=17)")
            if result.get("error_code"):
                raise RuntimeError(
                    f"Baidu OCR failed on page {page_num + 1}: "
                    f"{result.get('error_code')} {result.get('error_msg', '')}"
                )

            if "words_result" in result:
                for item in result["words_result"]:
                    results.append(item["words"])

        doc.close()
        return "\n".join(results)
