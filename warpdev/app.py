from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextLog


class WarpDevApp(App):
    """Minimal TUI inspired by Warp.dev."""

    CSS_PATH = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        self.log = TextLog(highlight=True)
        yield self.log
        yield Footer()

    async def on_mount(self) -> None:
        self.log.write("Warp.dev replica is under construction.")
        self.log.write("Integrate with Agent Zero APIs here.")


if __name__ == "__main__":
    WarpDevApp().run()
