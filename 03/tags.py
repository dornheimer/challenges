import collections
import difflib
from operator import itemgetter
import itertools
import re
import time
import xml.etree.ElementTree as ET

TOP_NUMBER = 10
RSS_FEED = 'rss.xml'
SIMILAR = 0.87


def time_it(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Elapsed time for {}: {}".format(func.__name__, end-start))
        return result
    return inner


@time_it
def get_tags():
    """Find all tags in RSS_FEED.
    Replace dash with whitespace."""
    xml_tree = ET.parse(RSS_FEED)
    root = xml_tree.getroot()
    items = root.getchildren()[0].getchildren()

    tags = {}
    for item in items:
        children = item.getchildren()
        for child in children:
            if child.tag == "category":
                tag = child.text.replace("-", " ").lower()
                tags[tag] = tags.get(tag, 0) + 1

    return tags


@time_it
def get_tags_re():
    tag_regex = re.compile(r"<category>([^<]+)</category>")
    with open(RSS_FEED) as f:
        tag_list = tag_regex.findall(f.read().lower())

    tags = {}
    for tag in tag_list:
        tag = tag.replace("-", " ")
        tags[tag] = tags.get(tag, 0) + 1

    return tags


@time_it
def get_top_tags(tags):
    """Get the TOP_NUMBER of most common tags"""
    # ~3x faster
    return list(sorted(tags.items(), key=itemgetter(1), reverse=True))[:TOP_NUMBER]


@time_it
def get_top_tags_counter(tags):
    """Get the TOP_NUMBER of most common tags"""
    return collections.Counter(tags).most_common(TOP_NUMBER)


@time_it
def get_similarities(tags):
    """Find set of tags pairs with similarity ratio of > SIMILAR"""
    similar_tags = set()
    for tag_a, tag_b in itertools.combinations(tags, 2):
        if tag_a[0] != tag_b[0]:  # ~12x faster
            continue
        ratio = difflib.SequenceMatcher(None, tag_a, tag_b).ratio()
        if ratio > SIMILAR:
            similar_tags.add((tag_a, tag_b))

    return similar_tags


if __name__ == "__main__":
    # tags = get_tags()
    tags = get_tags_re()  # ~2x faster
    top_tags = get_top_tags(tags)
    get_top_tags_counter(tags)
    print('* Top {} tags:'.format(TOP_NUMBER))
    for tag, count in top_tags:
        print('{:<20} {}'.format(tag, count))
    similar_tags = dict(get_similarities(tags))
    print('* Similar tags:')
    for singular, plural in similar_tags.items():
        print('{:<20} {}'.format(singular, plural))
