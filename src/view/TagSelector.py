from PySimpleGUI import *
from src.model.Tag import Tag
from difflib import SequenceMatcher


class TagSelector:

    def __init__(self, selected_tags: Optional[list[Tag]] = None):
        self.selected_tags: list[Tag] = (
            selected_tags if selected_tags is not None else []
        )

        self.window: Optional[Window] = None

    def update_list_boxes(self) -> None:
        """
        Updates the two list boxes based on the selected tags.
        """
        if self.window is None:
            raise RuntimeError(
                "Cannot update list boxes because there is no active popup."
            )

        non_selected_tags: list[Tag] = []
        for tag in Tag.get_all():
            if tag not in self.selected_tags:
                non_selected_tags.append(tag)

        # If the user has entered nothing in the search box sort by occasional value then name
        if self.window["-TAG SEARCH-"].get() == "":
            recurring_tags: list[Tag] = []
            occasional_tags: list[Tag] = []

            for tag in non_selected_tags:
                if tag.occasional:
                    occasional_tags.append(tag)
                else:
                    recurring_tags.append(tag)

            recurring_tags.sort(key=lambda t: t.name)
            occasional_tags.sort(key=lambda t: t.name)

            non_selected_tags = recurring_tags + occasional_tags

        # If the user has entered something in the search box sort by similarity to searched text
        else:
            non_selected_tags.sort(
                key=lambda t: SequenceMatcher(
                    None, t.name, self.window["-TAG SEARCH-"].get()
                ).ratio(),
                reverse=True,
            )

        self.window["-SELECTED TAGS LISTBOX-"].update(values=self.selected_tags)
        self.window["-TAGS LISTBOX-"].update(values=non_selected_tags)

    def popup(self) -> None:
        """
        Creates a popup that allows this selector's tags to be edited.
        """
        self.window = Window(
            "Tag Selector", layout=self._layout_generator(), resizable=True
        )
        self.window.read(timeout=0)
        self.window["-TAG SEARCH-"].bind("<Return>", "Enter")
        self.update_list_boxes()

        previous_tags: list[Tag] = self.selected_tags

        while True:

            event, values = self.window.read()

            if event == WINDOW_CLOSED or event == "Exit":
                self.selected_tags = previous_tags
                break

            if event == "-DONE BUTTON-":
                break

            if event == "-TAG SEARCH-Enter":
                self.selected_tags.append(
                    self.window["-TAGS LISTBOX-"].get_list_values()[0]
                )
                self.update_list_boxes()

            if event == "-TAG SEARCH-":
                self.update_list_boxes()

            if event == "-TAGS LISTBOX-":
                self.selected_tags.append(values["-TAGS LISTBOX-"][0])
                self.update_list_boxes()

            if event == "-SELECTED TAGS LISTBOX-":
                self.selected_tags.remove(values["-SELECTED TAGS LISTBOX-"][0])
                self.update_list_boxes()

        self.window.close()
        self.window = None

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the input popup.

        :return: Layout for the input popup.
        """
        search_column: Column = Column(
            [
                [Text("All Tags")],
                [
                    Input(
                        key="-TAG SEARCH-",
                        enable_events=True,
                        expand_x=True,
                        size=(24, None),
                    )
                ],
                [
                    Listbox(
                        values=[],
                        key="-TAGS LISTBOX-",
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                    )
                ],
            ],
            expand_x=True,
            expand_y=True,
        )
        selected_column: Column = Column(
            [
                [Text("Selected Tags")],
                [
                    Listbox(
                        values=[],
                        key="-SELECTED TAGS LISTBOX-",
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                        size=(25, None),
                    )
                ],
            ],
            expand_x=True,
            expand_y=True,
        )
        return [
            [search_column, selected_column],
            [Button("Done", key="-DONE BUTTON-", expand_x=True)],
        ]
