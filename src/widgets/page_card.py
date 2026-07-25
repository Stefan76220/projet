from src.widgets.card import Card
import traceback


class PageCard(Card):

    def __init__(self, parent, page, on_open=None):

        self.page = page
        self.on_open = on_open

        numero = page.get("numero", 0)

        super().__init__(
            parent=parent,
            icon="📄",
            title=f"Page {numero:03d}",
            subtitle="Page vide",
            infos=[
                "État : Brouillon"
            ],
            action_text="Ouvrir",
            action_command=self.open_page
        )

    # ---------------------------------------------------------

    def open_page(self):

        print("[DEBUG] PageCard.open_page")
        print("[DEBUG] page :", self.page)
        print("[DEBUG] on_open :", self.on_open)

        try:

            if self.on_open is None:
                print("[DEBUG] Callback absent.")
                return

            print("[DEBUG] Appel du callback...")

            self.on_open(self.page)

            print("[DEBUG] Callback terminé.")

        except Exception:

            traceback.print_exc()