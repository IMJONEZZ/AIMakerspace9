"""
WebFetch Tool for Python

A robust web fetching tool that extracts content from URLs with support for:
- Multiple output formats (markdown, text, html)
- Content type detection and conversion
- HTML to Markdown conversion
- Text extraction from HTML (removes scripts, styles, etc.)
- Timeout handling
- Size limits
- URL validation

Based on the opencode TypeScript webfetch implementation.
"""

import re
from typing import Literal, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from markdownify import markdownify as md


MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5MB
DEFAULT_TIMEOUT = 30.0  # 30 seconds
MAX_TIMEOUT = 120.0  # 2 minutes


def validate_url(url: str) -> bool:
    """Validate that URL starts with http:// or https://"""
    return url.startswith("http://") or url.startswith("https://")


def get_accept_header(format: Literal["markdown", "text", "html"]) -> str:
    """Get appropriate Accept header based on requested format"""
    if format == "markdown":
        return "text/markdown;q=1.0, text/x-markdown;q=0.9, text/plain;q=0.8, text/html;q=0.7, */*;q=0.1"
    elif format == "text":
        return "text/plain;q=1.0, text/markdown;q=0.9, text/html;q=0.8, */*;q=0.1"
    else:  # html
        return "text/html;q=1.0, application/xhtml+xml;q=0.9, text/plain;q=0.8, text/markdown;q=0.7, */*;q=0.1"


def extract_text_from_html(html: str) -> str:
    """Extract plain text from HTML, removing scripts, styles, and other non-content elements"""
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for element in soup(["script", "style", "noscript", "iframe", "object", "embed"]):
        element.decompose()

    # Get text and clean up
    text = soup.get_text(separator=" ", strip=True)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def convert_html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown using markdownify"""
    # First, remove unwanted elements
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "meta", "link"]):
        element.decompose()

    # Convert to markdown
    clean_html = str(soup)
    return md(clean_html, heading_style="ATX", bullets="-")


def _webfetch_impl(
    url: str,
    format: Literal["markdown", "text", "html"] = "markdown",
    timeout: Optional[int] = None,
) -> str:
    """
    Implementation of webfetch function.

    Fetches content from a specified URL and returns it in the requested format.

    Args:
        url: The URL to fetch content from. Must start with http:// or https://
        format: The format to return the content in. Options:
            - "markdown" (default): Converts HTML to Markdown
            - "text": Extracts plain text from HTML
            - "html": Returns raw HTML content
        timeout: Optional timeout in seconds (max 120). Defaults to 30.

    Returns:
        The fetched content in the requested format.

    Raises:
        ValueError: If URL is invalid or timeout exceeds maximum
        httpx.HTTPError: If the HTTP request fails

    Examples:
        >>> _webfetch_impl("https://example.com")
        "# Example Domain\n\nThis is an example..."

        >>> _webfetch_impl("https://example.com", format="text")
        "Example Domain This is an example..."
    """
    # Validate URL
    if not validate_url(url):
        raise ValueError("URL must start with http:// or https://")

    # Validate and set timeout
    if timeout is not None:
        if timeout > MAX_TIMEOUT:
            raise ValueError(f"Timeout cannot exceed {MAX_TIMEOUT} seconds")
    else:
        timeout = int(DEFAULT_TIMEOUT)

    # Parse URL for error messages
    parsed_url = urlparse(url)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Accept": get_accept_header(format),
            "Accept-Language": "en-US,en;q=0.9",
        }

        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            response = client.get(url, headers=headers)

            if not response.is_success:
                raise httpx.HTTPError(
                    f"Request failed with status code: {response.status_code}"
                )

            # Check content length
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > MAX_RESPONSE_SIZE:
                raise ValueError(
                    f"Response too large (exceeds {MAX_RESPONSE_SIZE // 1024 // 1024}MB limit)"
                )

            content = response.text
            if len(content.encode("utf-8")) > MAX_RESPONSE_SIZE:
                raise ValueError(
                    f"Response too large (exceeds {MAX_RESPONSE_SIZE // 1024 // 1024}MB limit)"
                )

            # Get content type
            content_type = response.headers.get("content-type", "")

            # Handle content based on requested format
            if format == "markdown":
                if "text/html" in content_type:
                    return convert_html_to_markdown(content)
                return content

            elif format == "text":
                if "text/html" in content_type:
                    return extract_text_from_html(content)
                return content

            else:  # html
                return content

    except httpx.TimeoutException:
        raise ValueError(f"Request timed out after {timeout} seconds")
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPError(
            f"HTTP error {e.response.status_code}: {e.response.reason_phrase}"
        )
    except Exception as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")


# Create the LangChain tool wrapper
webfetch_tool = tool(_webfetch_impl)

# Export both the raw function and the LangChain tool
__all__ = ["webfetch", "webfetch_tool"]

# For backwards compatibility, alias the raw function as webfetch
webfetch = _webfetch_impl
