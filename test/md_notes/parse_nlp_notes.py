from __future__ import annotations
from typing import List, Tuple
from common_utils.base.basic import BasicLoadableObject, \
    BasicLoadableHandler, BasicHandler
from jp_dict.anki.connect import AnkiConnect
from jp_dict.anki.model_structs import CardTemplateList, CardTemplate
from jp_dict.anki.note_structs import NoteAddParam

class StudyNoteFields(BasicLoadableObject['StudyNoteFields']):
    def __init__(
        self,
        front: str,
        back_bullets: str,
        category: str="",
        subcategory: str=""
    ):
        super().__init__()
        self.front = front
        self.back_bullets = back_bullets
        self.category = category
        self.subcategory = subcategory
    
    def _get_bracket_contents(self, text: str, left_bracket: str='[', right_bracket: str=']') -> str:
        # text.split(']')[0].split('[')[1]
        right_split = text.split(right_bracket)
        if len(right_split) <= 1:
            return ""
        left_split = right_split[0].split(left_bracket)
        if (len(left_split) <= 1):
            return ""
        return left_bracket.join(left_split[1:])
    
    def md_link_to_html(self, text: str) -> str:
        result = text
        while True:
            title_contents = self._get_bracket_contents(
                text=result,
                left_bracket='[', right_bracket=']'
            )
            url_contents = self._get_bracket_contents(
                text=result,
                left_bracket='(', right_bracket=')'
            )
            md_url_text = f'[{title_contents}]({url_contents})'
            if title_contents == "" or url_contents == "" or md_url_text not in result:
                break
            html_link = f'<a href="{url_contents}">{title_contents}</a>'
            result = result.replace(md_url_text, html_link)
        return result
    
    def convert_md_links_to_html(self):
        self.category = self.md_link_to_html(self.category)
        self.subcategory = self.md_link_to_html(self.subcategory)
        self.front = self.md_link_to_html(self.front)
        self.back_bullets = self.md_link_to_html(self.back_bullets)

class StudyNoteFieldsList(
    BasicLoadableHandler['StudyNoteFieldsList', 'StudyNoteFields'],
    BasicHandler['StudyNoteFieldsList', 'StudyNoteFields']
):
    def __init__(self, fields_list: List[StudyNoteFields]=None):
        super().__init__(obj_type=StudyNoteFields, obj_list=fields_list)
        self.fields_list = self.obj_list
    
    @classmethod
    def from_dict_list(cls, dict_list: List[dict]) -> StudyNoteFieldsList:
        return StudyNoteFieldsList([StudyNoteFields.from_dict(item_dict) for item_dict in dict_list])

    def convert_md_links_to_html(self):
        for fields in self:
            fields.convert_md_links_to_html()

    def from_md_path(path: str) -> StudyNoteFieldsList:
        f = open(path, 'r')
        fields_list = StudyNoteFieldsList()
        current_category = ""
        current_subcategory = ""
        current_front = ""
        previous_front = ""
        current_back_bullet_list = []
        ignoreBullets = False
        for line in f.readlines():
            line = line.replace('\t', '')
            line = line.replace('   ', '')
            line = line.replace('\n', '')
            isFrontFlag = False
            isBackFlag = False
            isCategoryFlag = False
            isSubcategoryFlag = False
            if line.replace(' ', '').startswith('##'):
                subcategory = line.replace("## ", "").replace("#", "")
                print(f'Subcategory: {subcategory}')
                current_subcategory = subcategory
                isSubcategoryFlag = True
            elif line.replace(' ', '').startswith('#'):
                category = line.replace("# ", "").replace("#", "")
                print(f'Category: {category}')
                current_category = category
                isCategoryFlag = True
            elif line.replace(' ', '').startswith('*[]'):
                front = line.replace("* [ ] ", "")
                print(f'Front: {front}')
                previous_front = current_front
                current_front = front
                isFrontFlag = True
                ignoreBullets = False
            elif line.replace(' ', '').startswith('*[x]'):
                ignoreBullets = True
            elif line.replace(' ', '').startswith('*'):
                if not ignoreBullets:
                    back_bullet = line.replace("* ", "")
                    print(f'Back bullet: {back_bullet}')
                    current_back_bullet_list.append(back_bullet)
                    isBackFlag = True
            else:
                # print(line)
                pass

            if not isBackFlag and len(current_back_bullet_list) > 0:
                bullet_list_text = ""
                if len(current_back_bullet_list) > 0:
                    bullet_list_text += "<ul>"
                    for text in current_back_bullet_list:
                        bullet_list_text += f"<li>{text}</li>"
                    bullet_list_text += "</ul>"
                fields = StudyNoteFields(
                    front=previous_front if isFrontFlag else current_front,
                    back_bullets=bullet_list_text,
                    category=current_category,
                    subcategory=current_subcategory
                )
                fields_list.append(fields)
                current_front = "" if not isFrontFlag else current_front
                current_back_bullet_list = []
        if len(current_back_bullet_list) > 0:
            bullet_list_text = ""
            if len(current_back_bullet_list) > 0:
                bullet_list_text += "<ul>"
                for text in current_back_bullet_list:
                    bullet_list_text += f"<li>{text}</li>"
                bullet_list_text += "</ul>"
            fields = StudyNoteFields(
                front=current_front,
                back_bullets=bullet_list_text,
                category=current_category,
                subcategory=current_subcategory
            )
            fields_list.append(fields)
        f.close()
        fields_list.convert_md_links_to_html()
        return fields_list
    
    @property
    def model_name(self) -> str:
        return 'parsed_markdown'

    def init_anki_model(self):
        from textwrap import dedent
        anki_connect = AnkiConnect()
        if self.model_name not in anki_connect.get_model_names():
            anki_connect.create_model(
                model_name=self.model_name,
                field_names=StudyNoteFields.get_constructor_params(),
                css=dedent("""
                .card {
                    font-family: arial;
                    font-size: 20px;
                    text-align: center;
                    color: black;
                    background-color: white;
                }
                """),
                card_templates=CardTemplateList([
                    CardTemplate(
                        name='Card 1',
                        front=dedent("""
                        {{front}}
                        """),
                        back=dedent("""
                        {{front}}
                        <hr id=answer>
                        {{back_bullets}}
                        <br><br>
                        Category: {{category}}
                        <br>
                        Subcategory: {{subcategory}}
                        """)
                    )
                ])
            )

    def add_to_anki_deck(self, deck_name: str, **kwargs):
        anki_connect = AnkiConnect()
        self.init_anki_model()
        if deck_name not in anki_connect.get_deck_names():
            anki_connect.create_deck(deck_name)
        for fields in self:
            note = NoteAddParam.from_fields(
                deck_name=deck_name,
                model_name=self.model_name,
                fields=fields,
                **kwargs
            )
            anki_connect.add_note(note)

fields_list = StudyNoteFieldsList.from_md_path('nlp_notes.md')
relevant_fields_list = fields_list.get(category='Natural Language Processing with PyTorch: Build Intelligent Language Applications Using Deep Learning (2019)')
relevant_fields_list.save_to_path('nlp_notes-nlp_with_pytorch.json', overwrite=True)
relevant_fields_list.add_to_anki_deck('nlp_notes-nlp_with_pytorch')