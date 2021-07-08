from jp_dict.anki.md_notes import StudyNoteFieldsList

fields_list = StudyNoteFieldsList.from_md_path('nlp_notes.md')
relevant_fields_list = fields_list.get(category='Natural Language Processing with PyTorch: Build Intelligent Language Applications Using Deep Learning (2019)')
relevant_fields_list.save_to_path('nlp_notes-nlp_with_pytorch.json', overwrite=True)
relevant_fields_list.add_to_anki_deck('nlp_notes-nlp_with_pytorch')