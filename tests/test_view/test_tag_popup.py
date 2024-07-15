"""
Tests for the TagPopup class.
"""

# mypy: ignore-errors
from PySimpleGUI import Window
from ddt import ddt, data

from src.model.tag import Tag
from src.view.tag_popup import TagPopup
from tests.test_model.sample_1_test_case import Sample1TestCase


@ddt
class TestTagPopup(Sample1TestCase):
    """
    Tests for the TagPopup class.
    """

    def test_construction_for_new_tag(self):
        """
        Tests the constructor for a new tag.
        """
        popup: TagPopup = TagPopup(None)
        popup_window: Window = popup.window
        _, _ = popup_window.read(timeout=0)

        # Validate basic fields and inputs
        self.assertEqual("", popup_window[TagPopup.NAME_INPUT_KEY].get())
        self.assertFalse(popup_window[TagPopup.OCCASIONAL_CHECKBOX_KEY].get())
        self.assertEqual("", popup_window[TagPopup.RULE_INPUT_KEY].get())

        self.assertFalse(popup.inputs_valid())

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    def test_construction_with_existing_tag(self, tag_id: int):
        """
        Tests the construction of a tag popup from an existing tag.
        """
        tag: Tag = Tag.from_id(tag_id)
        popup: TagPopup = TagPopup(Tag.from_id(tag_id))
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        self.assertEqual(tag.name, popup_window[TagPopup.NAME_INPUT_KEY].get())
        self.assertEqual(
            tag.occasional, popup_window[TagPopup.OCCASIONAL_CHECKBOX_KEY].get()
        )
        self.assertEqual(
            "" if tag.rule is None else tag.rule,
            popup_window[TagPopup.RULE_INPUT_KEY].get(),
        )

        self.assertTrue(popup.inputs_valid())

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    def test_submit_unchanged_tag(self, tag_id: int):
        """
        Tests submitting a tag popup with no changes.
        """
        expected_tags: list[Tag] = Tag.get_all()

        popup: TagPopup = TagPopup(Tag.from_id(tag_id))
        _, _ = popup.window.read(timeout=0)
        popup.check_event(TagPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_tags, Tag.get_all())

        popup.window.close()

    def test_close_after_edits(self):
        """
        Tests making edits to the tag popup then closing it.
        """
        expected_tags: list[Tag] = Tag.get_all()

        popup: TagPopup = TagPopup(Tag.from_id(6))

        # Fake user inputs
        new_name: str = "Paid for by parents"
        popup.window[TagPopup.NAME_INPUT_KEY].update(new_name)
        popup.check_event(TagPopup.NAME_INPUT_KEY, {TagPopup.NAME_INPUT_KEY: new_name})

        new_occasional: bool = True
        popup.window[TagPopup.OCCASIONAL_CHECKBOX_KEY].update(new_occasional)
        popup.check_event(
            TagPopup.OCCASIONAL_CHECKBOX_KEY,
            {TagPopup.OCCASIONAL_CHECKBOX_KEY: new_occasional},
        )

        new_rule: str = ""
        popup.window[TagPopup.RULE_INPUT_KEY].update(new_rule)
        popup.check_event(TagPopup.RULE_INPUT_KEY, {TagPopup.RULE_INPUT_KEY: new_rule})

        popup.check_event("Exit", {})

        self.assertSqlListEqual(expected_tags, Tag.get_all())

        popup.window.close()

    def test_submit_edited_tag(self):
        """
        Tests editing the database with the basic inputs fields.
        """
        expected_tags: list[Tag] = Tag.get_all()
        expected_tags[5] = Tag(6, "Paid for by parents", True, None)

        popup: TagPopup = TagPopup(Tag.from_id(6))

        # Fake user inputs
        new_name: str = "Paid for by parents"
        popup.window[TagPopup.NAME_INPUT_KEY].update(new_name)
        popup.check_event(TagPopup.NAME_INPUT_KEY, {TagPopup.NAME_INPUT_KEY: new_name})

        new_occasional: bool = True
        popup.window[TagPopup.OCCASIONAL_CHECKBOX_KEY].update(new_occasional)
        popup.check_event(
            TagPopup.OCCASIONAL_CHECKBOX_KEY,
            {TagPopup.OCCASIONAL_CHECKBOX_KEY: new_occasional},
        )

        new_rule: str = ""
        popup.window[TagPopup.RULE_INPUT_KEY].update(new_rule)
        popup.check_event(TagPopup.RULE_INPUT_KEY, {TagPopup.RULE_INPUT_KEY: new_rule})

        popup.check_event(TagPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_tags, Tag.get_all())

        popup.window.close()
