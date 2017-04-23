import markdown
import re
import csv
import sys
from mdx_gfm import GithubFlavoredMarkdownExtension

def split_heading_level(md, level):
    """Given a markdown string, extracts a list of all (heading, content) pairs with the given level/depth"""
    pattern = r"^#{"+str(level)+r"}(?!#)"
    parts = re.split(pattern, md, flags=re.M)
    parts = [p.strip() for p in parts[1:]]
    results = []
    for p in parts:
        lines = p.split('\n')
        results.append((lines[0].strip(), "\n".join(lines[1:])))
    return results

def parse_question(heading, content):
    subheadings = split_heading_level(content, 4)
    heading_map = {}
    heading_map['heading'] = heading
    for subheading, subcontent in subheadings:
        heading_map[subheading.lower().strip()] = subcontent.strip()
    if 'question' not in heading_map:
        heading_map['question'] = heading_map['heading']
    if 'uuid' not in heading_map:
        heading_map['uuid'] = heading_map['heading']
    if 'answer' not in heading_map:
        heading_map['answer'] = ''
    return heading_map

def parse_deck(heading, content):
    subheadings = split_heading_level(content, 2)
    heading_map = {}
    heading_map['heading'] = heading
    for subheading, subcontent in subheadings:
        lines = subcontent.split('\n')
        heading_map[subheading.lower().strip()] = subcontent
    question_headings = split_heading_level(heading_map['questions'], 3)
    heading_map['questions'] = [parse_question(*q) for q in question_headings]
    return heading_map

def md_to_html(md):
    return markdown.markdown(md,
                             extensions=[GithubFlavoredMarkdownExtension()])

def write_anki_csv(decks, file_path):
    def write_deck(deck):
        for q in deck['questions']:
            write_question(q)
    def write_question(question):
        uuid = question['uuid']
        desc = question['question']
        ans = question['answer']
        writer.writerow([uuid, desc, ans])
    with open(file_path, 'w+') as f:
        writer = csv.writer(f, delimiter=';')
        for d in decks:
            write_deck(d)

def process_question(question):
    question['question'] = md_to_html(re.sub('\n', '<br/>', question['question']))
    question['answer'] = md_to_html(re.sub('\n', '<br/>', question['answer']))

def process(md):
    """Converts a markdown string to a CSV format accepted by anki"""
    decks = split_heading_level(md, 1)
    result = []
    for name, deck_md in decks:
        deck = parse_deck(name, deck_md)
        for q in deck['questions']:
            process_question(q)
        result.append(deck)
    return result

def main():
    inp = sys.argv[1]
    out = sys.argv[2]
    md = open(inp).read()
    decks = process(md)
    write_anki_csv(decks, out)

def test():
    md = open('example.md').read()
    decks = process(md)
    write_anki_csv(decks, 'example.csv')

if __name__ == '__main__':
    main()
else:
    test()
