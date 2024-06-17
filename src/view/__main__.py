from PySimpleGUI import *
from pathlib import Path

from src.model.Tag import Tag
from src.model import database
from src.model.Transaction import Transaction

database.connect(
    Path("/Users/Marcus/Desktop/ExTrack/tests/test_data/sample_database_1.db")
)

window: Window = Window("Transaction")


class Row:

    def __init__(self, sqlid: int, name: str, occasional: bool) -> None:
        self.sqlid: int = sqlid
        self.name: str = name
        self.occasional: bool = occasional

        self.name_input: Input = Input(
            default_text=self.name, key=("-NAME-", self.sqlid), enable_events=True
        )
        self.occasional_button: Button = Button(
            "Occasional" if self.occasional else "Recurring",
            key=("-OCCASIONAL-", self.sqlid),
        )

    def get(self) -> any:
        return [
            pin(
                Col(
                    [[Text(self.sqlid), self.name_input, self.occasional_button]],
                    key=("-COL-", self.sqlid),
                )
            )
        ]

    def check_event(self, event: any, values: dict):

        if event == ("-NAME-", self.sqlid):
            print(f"{self.sqlid}NAME: {event} {values}")

        if event == ("-OCCASIONAL-", self.sqlid):
            print(f"{self.sqlid}OCCASIONAL: {event} {values}")
            self.occasional_button.update(
                text=(
                    "Occasional"
                    if self.occasional_button.get_text() == "Recurring"
                    else "Recurring"
                )
            )


rows = list(Row(tag.sqlid, tag.name, tag.occasional) for tag in Tag.get_all())

layout = [
    [Text("Tags Table")],
    [Col([row.get() for row in rows], scrollable=True, expand_x=True, expand_y=True)],
]

window = Window("Test", layout, resizable=True)

while True:

    event, values = window.read()

    if event == WINDOW_CLOSED or event == "Exit":
        break

    for row in rows:
        row.check_event(event, values)

window.close()

# ======================================================================================================================

# transaction_data: list[list[str]] = list(
#     [
#         str(trans.sqlid),
#         trans.account().name,
#         trans.description,
#         trans.merchant().name if trans.merchant_id else "None",
#         trans.date.strftime("%a %b %d %Y"),
#     ]
#     for trans in Transaction.get_all()
# )
#
# transaction_tab_layout: list[list[Element]] = [
#     [
#         Table(
#             values=transaction_data,
#             headings=["id", "Account", "Description", "Merchant", "Date"],
#             expand_y=True,
#             expand_x=True,
#             enable_events=True,
#             key="-TRANS TABLE-",
#         )
#     ]
# ]
#
# window: Window = Window(
#     title="ExTrack", layout=transaction_tab_layout, size=(1000, 500), resizable=True
# )
#
# while True:
#     event, values = window.read()
#
#     if event == WINDOW_CLOSED or event == "Exit":
#         break
#
#     if event == "-TRANS TABLE-":
#         row_index: int = values["-TRANS TABLE-"][0]
#
# window.close()
