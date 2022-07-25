import streamlit as st

class MakerView: 
    """
    MakerView streamlit class for multipage support
    """

    def __init__(self) -> None:
        """
        Initializes storage of application pages
        """
        self.pages = []
    
    def add_page(self, title, func) -> None: 
        """ 
        Method to add new MakerView pages

        Params:
            title (str): Page title
            
            func: Page rendering function
        """

        self.pages.append({
                "title": title, 
                "function": func
            })

    def run(self):
        """
        Run streamlit configuration
        """

        page = st.sidebar.selectbox(
            'Select page', 
            self.pages, 
            format_func=lambda page: page['title']
        )

        page['function']()