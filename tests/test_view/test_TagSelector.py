from tests.test_model.Sample1TestCase import Sample1TestCase
from src.model.Tag import Tag
from src.view.TagSelector import TagSelector
from ddt import ddt, data, unpack


@ddt
class TestTagSelector(Sample1TestCase):

    @data(
        ("", [11, 5, 7, 2, 1, 10, 6, 4, 3, 9, 8]),
        ("gas", [2, 5, 3, 10, 1, 4, 6, 7, 9, 8, 11]),
        ("the ", [9, 8, 7, 5, 11, 10, 1, 6, 4, 2, 3]),
        ("hello", [10, 9, 11, 1, 6, 4, 8, 2, 3, 5, 7]),
    )
    @unpack
    def test_search(self, search_value: str, expected_id_list: list[int]):
        """
        Test the tag search input feature.

        Prerequisites: None

        :param search_value: Value to enter into the search box
        :param expected_id_list: List of expected tag ids ordered depending on similarity to the search_value
        """
        tag_selector: TagSelector = TagSelector()
        tag_selector.window.read(timeout=0)

        tag_selector.window["-TAG SEARCH-"].update(value=search_value)
        tag_selector.check_event("-TAG SEARCH-", None)

        self.assertSqlListEqual(
            list(Tag.from_id(sqlid) for sqlid in expected_id_list),
            tag_selector.window["-TAGS LISTBOX-"].get_list_values(),
        )

    @data(
        ("", [5, 7, 2, 1, 10, 6, 4, 3, 9, 8], [11]),
        ("gas", [5, 3, 10, 1, 4, 6, 7, 9, 8, 11], [2]),
        ("the ", [8, 7, 5, 11, 10, 1, 6, 4, 2, 3], [9]),
        ("hello", [9, 11, 1, 6, 4, 8, 2, 3, 5, 7], [10]),
    )
    @unpack
    def test_select_with_enter(
        self,
        search_value: str,
        expected_non_selected_id_list: list[int],
        expected_selected_id_list: list[int],
    ):
        """
        Tests selecting the first item in the non-selected list with the enter key.

        Prerequisites: test_search

        :param search_value: Value to enter into the search box
        :param expected_non_selected_id_list: Expected list of non-selected tag ids
        :param expected_selected_id_list: Expected list of selected tag ids
        """
        tag_selector: TagSelector = TagSelector()
        tag_selector.window.read(timeout=0)

        tag_selector.window["-TAG SEARCH-"].update(value=search_value)
        tag_selector.check_event("-TAG SEARCH-", None)
        tag_selector.check_event("-TAG SEARCH-ENTER", None)

        self.assertSqlListEqual(
            list(Tag.from_id(sqlid) for sqlid in expected_non_selected_id_list),
            tag_selector.window["-TAGS LISTBOX-"].get_list_values(),
        )
        self.assertSqlListEqual(
            list(Tag.from_id(sqlid) for sqlid in expected_selected_id_list),
            tag_selector.window["-SELECTED TAGS LISTBOX-"].get_list_values(),
        )

    # TODO Write test for selecting values by clicking in the list box

    # TODO Write test for deselecting values by clicking in the selected list box

    # TODO Write test for submitting values via the done button

    # TODO Write test for canceling values via the X button
