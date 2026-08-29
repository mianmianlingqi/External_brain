from urllib.request import urlopen
from urllib.error import HTTPError

import pytest

from brain import ViewDenied, init, render_html, start_view_server, view_snapshot


def test_wrong_secret_hides_progress():
    brain = init("analog-electronics")
    with pytest.raises(ViewDenied):
        view_snapshot(brain, "view-secret", "nope")


def test_view_lists_directions_then_matches_brain_queries():
    brain = init("analog-electronics")
    brain.add_direction("italian")
    listing = view_snapshot(brain, "view-secret", "view-secret")
    assert listing.directions == ("analog-electronics", "italian")
    assert listing.review is None
    page = view_snapshot(brain, "view-secret", "view-secret", direction="analog-electronics")
    assert page.review == brain.review("analog-electronics")
    assert page.graph == brain.graph("analog-electronics")
    listing_html = render_html(listing)
    assert "italian" in listing_html
    page_html = render_html(page)
    assert "clear 0" in page_html


def test_http_view_needs_secret_and_stays_up():
    brain = init("analog-electronics")
    brain.add_direction("italian")
    url, stop = start_view_server(brain, "view-secret")
    try:
        with pytest.raises(HTTPError) as denied:
            urlopen(url.split("?")[0] + "?secret=nope")
        assert denied.value.code == 403
        listing = urlopen(url, timeout=2).read().decode("utf-8")
        assert "italian" in listing
        page = urlopen(url + "&direction=analog-electronics", timeout=2).read().decode("utf-8")
        assert "clear 0" in page
    finally:
        stop()
