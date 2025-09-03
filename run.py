import customtkinter as ctk
from src.prism2.gui.main_view import MainView
from src.prism2.view_models.main_view_model import MainViewModel


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Prism2")
        self.geometry("1024x768")

        # The ViewModel and MainView will be created after the root window exists.
        self.view_model = MainViewModel()
        self.main_view = MainView(self, self.view_model)
        self.main_view.pack(side="top", fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    # Create and run the application
    app = Application()
    app.mainloop()
