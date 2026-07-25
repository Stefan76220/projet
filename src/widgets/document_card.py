from src.widgets.card import Card


class DocumentCard(Card):

    def __init__(self, parent, document, on_open=None):

        self.document = document
        self.on_open = on_open

        super().__init__(
            parent=parent,
            icon="📘",
            title=document["nom"],
            subtitle=document.get("type", "Document"),
            infos=[
                "0 page"
            ],
            action_text="Ouvrir",
            action_command=self.open_document
        )

    # ---------------------------------------------------------

    def open_document(self):

        if self.on_open is not None:
            self.on_open(self.document)