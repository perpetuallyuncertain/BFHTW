from lxml import etree
from pathlib import Path
from typing import List, Dict, Generator, Optional

ROOT_DIR = Path(__file__).parents[3]

file_path = ROOT_DIR / "BFHTW/sources/pubmed_pmc/temp/extract_PMC17816/PMC17816/ar-2-5-399.nxml"

class PubMedNXMLParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.tree = etree.parse(str(self.file_path), parser=None)
        self.root = self.tree.getroot()

        pretty_xml = etree.tostring(self.root, pretty_print=True, encoding="unicode")
        
        with open('test_nxml.txt', 'w') as f:
            f.write(pretty_xml)
        import pdb; pdb.set_trace()

    def list_all_tags(self) -> List[str]:
        return print(set(elem.tag for elem in self.root.iter()))

    def get_metadata(self) -> Dict[str, Optional[str]]:
        def x(path):  # Small helper
            el = self.root.xpath(path)
            return el[0].text.strip() if el else None

        return {
            "pmcid": x(".//article-id[@pub-id-type='pmc']"),
            "doi": x(".//article-id[@pub-id-type='doi']"),
            "title": x(".//article-title"),
            "journal": x(".//journal-title"),
            "pub_date": x(".//pub-date/year"),
        }

    def extract_blocks(self) -> Generator[Dict[str, str], None, None]:
        section_counter = 0
        for sec in self.root.xpath(".//body//sec"):
            section_counter += 1
            section_title_el = sec.find("title")
            section_title = section_title_el.text.strip() if section_title_el is not None else None

            for para in sec.findall("p"):
                yield {
                    "section_index": section_counter,
                    "section_title": section_title,
                    "text": "".join(para.itertext()).strip()
                }
    
    def dump_text_nodes(self, max=50):
        for i, el in enumerate(self.root.iter()):
            if el.text and el.text.strip():
                path = self.tree.getpath(el)
                text = el.text.strip().replace("\n", " ")[:80]
                print(f"{path} → {text}")
            if i > max:
                break



parser = PubMedNXMLParser(file_path=str(file_path))

parser.dump_text_nodes()


