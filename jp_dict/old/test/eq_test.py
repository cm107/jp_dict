from ..util.decorators import assert_test_classmethod
from ..lib.jisho.misc import Notes, Link
from ..lib.jisho.jap_vocab import JapaneseVocab, OtherForm, OtherForms
from ..lib.jisho.supplemental_info import CategoryLabel, SeeAlsoLink, RestrictionInfo, AdditionalInfo, AntonymLink, SourceInfo, SupplementalInfo
from ..lib.jisho.definition import DefinitionSection, DefinitionGroup, Definitions
from ..lib.jisho.concept import ConceptLabels
from ..lib.jisho.vocab_entry import VocabularyEntry
from ..lib.jisho.word_results import WordResult, WordResultHandler

class EqualityTest:
    def __init__(self):
        pass

    @assert_test_classmethod
    def notes_eq_test(self):
        notes_0 = Notes(text='Note A')
        notes_1 = Notes(text='Note B')
        notes_2 = Notes(text='Note A')
        assert notes_0 != notes_1
        assert notes_0 == notes_2
        assert notes_0 == notes_0.copy()

    @assert_test_classmethod
    def link_eq_test(self):
        link_0 = Link(text='Text A', url='URL A')
        link_1 = Link(text='Text A', url='URL A')
        link_2 = Link(text='Text B', url='URL A')
        link_3 = Link(text='Text A', url='URL B')
        link_4 = Link(text='Text B', url='URL B')
        assert link_0 == link_1
        assert link_0 != link_2
        assert link_0 != link_3
        assert link_0 != link_4
        assert link_0 == link_0.copy()

    @assert_test_classmethod
    def jap_vocab_eq_test(self):
        jap_vocab_0 = JapaneseVocab(writing='Writing A', reading='Reading A')
        jap_vocab_1 = JapaneseVocab(writing='Writing A', reading='Reading A')
        jap_vocab_2 = JapaneseVocab(writing='Writing B', reading='Reading A')
        jap_vocab_3 = JapaneseVocab(writing='Writing A', reading='Reading B')
        jap_vocab_4 = JapaneseVocab(writing='Writing B', reading='Reading B')
        assert jap_vocab_0 == jap_vocab_1
        assert jap_vocab_0 != jap_vocab_2
        assert jap_vocab_0 != jap_vocab_3
        assert jap_vocab_0 != jap_vocab_4
        assert jap_vocab_0 == jap_vocab_0.copy()

    @assert_test_classmethod
    def other_form_eq_test(self):
        other_form_0 = OtherForm(kanji_writing='Kanji Writing A', kana_writing='Kana Writing A')
        other_form_1 = OtherForm(kanji_writing='Kanji Writing A', kana_writing='Kana Writing A')
        other_form_2 = OtherForm(kanji_writing='Kanji Writing B', kana_writing='Kana Writing A')
        other_form_3 = OtherForm(kanji_writing='Kanji Writing A', kana_writing='Kana Writing B')
        other_form_4 = OtherForm(kanji_writing='Kanji Writing B', kana_writing='Kana Writing B')
        assert other_form_0 == other_form_1
        assert other_form_0 != other_form_2
        assert other_form_0 != other_form_3
        assert other_form_0 != other_form_4
        assert other_form_0 == other_form_0.copy()

    @assert_test_classmethod
    def other_forms_eq_test(self):
        other_form_0 = OtherForm(kanji_writing='Kanji Writing A', kana_writing='Kana Writing A')
        other_form_1 = OtherForm(kanji_writing='Kanji Writing A', kana_writing='Kana Writing A')
        other_form_2 = OtherForm(kanji_writing='Kanji Writing B', kana_writing='Kana Writing A')
        other_form_3 = OtherForm(kanji_writing='Kanji Writing A', kana_writing='Kana Writing B')
        other_form_4 = OtherForm(kanji_writing='Kanji Writing B', kana_writing='Kana Writing B')

        other_forms_0 = OtherForms(other_form_list=[other_form_0, other_form_2, other_form_3]) # base
        other_forms_1 = OtherForms(other_form_list=[other_form_1, other_form_2, other_form_3]) # eq
        other_forms_2 = OtherForms(other_form_list=[other_form_3, other_form_1, other_form_2]) # neq
        other_forms_3 = OtherForms(other_form_list=[other_form_3, other_form_4, other_form_1, other_form_2]) # neq
        other_forms_4 = OtherForms(other_form_list=[other_form_3, other_form_4, other_form_2]) # neq
        other_forms_5 = OtherForms(other_form_list=[other_form_0, other_form_0, other_form_0]) # neq
        other_forms_6 = OtherForms(other_form_list=[other_form_4, other_form_4, other_form_4]) # neq

        assert other_forms_0 == other_forms_1
        assert other_forms_0 != other_forms_2
        assert other_forms_0 != other_forms_3
        assert other_forms_0 != other_forms_4
        assert other_forms_0 != other_forms_5
        assert other_forms_0 != other_forms_6
        assert other_forms_0 == other_forms_0.copy()

    @assert_test_classmethod
    def category_label_test(self):
        category_label_0 = CategoryLabel(text='Category Label A')
        category_label_1 = CategoryLabel(text='Category Label B')
        category_label_2 = CategoryLabel(text='Category Label B')
        assert category_label_0 != category_label_1
        assert category_label_1 == category_label_2

    @assert_test_classmethod
    def see_also_link_eq_test(self):
        see_also_link_0 = SeeAlsoLink(text='Text A', url='URL A')
        see_also_link_1 = SeeAlsoLink(text='Text A', url='URL A')
        see_also_link_2 = SeeAlsoLink(text='Text B', url='URL A')
        see_also_link_3 = SeeAlsoLink(text='Text A', url='URL B')
        see_also_link_4 = SeeAlsoLink(text='Text B', url='URL B')
        link0 = Link(text='Text A', url='URL A')
        link1 = Link(text='Text A', url='URL B')
        assert see_also_link_0 == see_also_link_1
        assert see_also_link_0 != see_also_link_2
        assert see_also_link_0 != see_also_link_3
        assert see_also_link_0 != see_also_link_4
        assert see_also_link_0 != link0
        assert see_also_link_0 != link1
        assert see_also_link_0 == see_also_link_0.copy()

    @assert_test_classmethod
    def restriction_info_eq_test(self):
        restriction_info_0 = RestrictionInfo(text='Restriction Info A')
        restriction_info_1 = RestrictionInfo(text='Restriction Info B')
        restriction_info_2 = RestrictionInfo(text='Restriction Info B')
        assert restriction_info_0 != restriction_info_1
        assert restriction_info_1 == restriction_info_2
        assert restriction_info_0 == restriction_info_0.copy()

    @assert_test_classmethod
    def additional_info_eq_test(self):
        additional_info_0 = AdditionalInfo(text='Additional Info A')
        additional_info_1 = AdditionalInfo(text='Additional Info B')
        additional_info_2 = AdditionalInfo(text='Additional Info B')
        assert additional_info_0 != additional_info_1
        assert additional_info_1 == additional_info_2
        assert additional_info_0 == additional_info_0.copy()

    @assert_test_classmethod
    def antonym_link_eq_test(self):
        antonym_link_0 = AntonymLink(text='Text A', url='URL A')
        antonym_link_1 = AntonymLink(text='Text A', url='URL A')
        antonym_link_2 = AntonymLink(text='Text B', url='URL A')
        antonym_link_3 = AntonymLink(text='Text A', url='URL B')
        antonym_link_4 = AntonymLink(text='Text B', url='URL B')
        link0 = Link(text='Text A', url='URL A')
        link1 = Link(text='Text A', url='URL B')
        assert antonym_link_0 == antonym_link_1
        assert antonym_link_0 != antonym_link_2
        assert antonym_link_0 != antonym_link_3
        assert antonym_link_0 != antonym_link_4
        assert antonym_link_0 != link0
        assert antonym_link_0 != link1
        assert antonym_link_0 == antonym_link_0.copy()

    @assert_test_classmethod
    def source_info_eq_test(self):
        source_info_0 = SourceInfo(text='Source Info A')
        source_info_1 = SourceInfo(text='Source Info B')
        source_info_2 = SourceInfo(text='Source Info B')
        assert source_info_0 != source_info_1
        assert source_info_1 == source_info_2
        assert source_info_0 == source_info_0.copy()

    @assert_test_classmethod
    def supplemental_info_eq_test(self):
        [supplemental_info_0, supplemental_info_1] = SupplementalInfo.sample(2)
        [supplemental_info_2] = SupplementalInfo.sample(1)
        assert supplemental_info_0 != supplemental_info_1
        assert supplemental_info_0 == supplemental_info_2
        assert supplemental_info_0 == supplemental_info_0.copy()

    @assert_test_classmethod
    def definition_section_eq_test(self):
        [def_section_0, def_section_1] = DefinitionSection.sample(2)
        [def_section_2] = DefinitionSection.sample(1)
        assert def_section_0 != def_section_1
        assert def_section_0 == def_section_2
        assert def_section_0 == def_section_0.copy()

    @assert_test_classmethod
    def definition_group_eq_test(self):
        [def_group_0, def_group_1] = DefinitionGroup.sample(2)
        [def_group_2] = DefinitionGroup.sample(1)
        assert def_group_0 != def_group_1
        assert def_group_0 == def_group_2
        assert def_group_0 == def_group_0.copy()

    @assert_test_classmethod
    def definitions_eq_test(self):
        [definitions_0, definitions_1] = Definitions.sample(2)
        [definitions_2] = Definitions.sample(1)
        assert definitions_0 != definitions_1
        assert definitions_0 == definitions_2
        assert definitions_0 == definitions_0.copy()

    @assert_test_classmethod
    def concept_labels_eq_test(self):
        [concept_labels_0, concept_labels_1] = ConceptLabels.sample(2)
        [concept_labels_2] = ConceptLabels.sample(1)
        assert concept_labels_0 != concept_labels_1
        assert concept_labels_0 == concept_labels_2
        concept_labels_0 = ConceptLabels.buffer(concept_labels_0)
        assert concept_labels_0 == concept_labels_0.copy()

    @assert_test_classmethod
    def vocab_entry_eq_test(self):
        [vocab_entry_0, vocab_entry_1] = VocabularyEntry.sample(2)
        [vocab_entry_2] = VocabularyEntry.sample(1)
        assert vocab_entry_0 != vocab_entry_1
        assert vocab_entry_0 == vocab_entry_2
        vocab_entry_0 = VocabularyEntry.buffer(vocab_entry_0)
        assert vocab_entry_0 == vocab_entry_0.copy()

    @assert_test_classmethod
    def word_result_eq_test(self):
        [word_result_0, word_result_1] = WordResult.sample(2)
        [word_result_2] = WordResult.sample(1)
        assert word_result_0 != word_result_1
        assert word_result_0 == word_result_2
        word_result_0 = WordResult.buffer(word_result_0)
        assert word_result_0 == word_result_0.copy()
        # from logger import logger
        # logger.purple(word_result_0)

    def test_all(self):
        self.notes_eq_test()
        self.link_eq_test()
        self.jap_vocab_eq_test()
        self.other_form_eq_test()
        self.other_forms_eq_test()
        self.category_label_test()
        self.see_also_link_eq_test()
        self.restriction_info_eq_test()
        self.additional_info_eq_test()
        self.antonym_link_eq_test()
        self.source_info_eq_test()
        self.supplemental_info_eq_test()
        self.definition_section_eq_test()
        self.definition_group_eq_test()
        self.definitions_eq_test()
        self.vocab_entry_eq_test()
        self.word_result_eq_test()