import pandas as pd
from weasyprint import HTML

from common.exceptions import exception_handler


class EtlService:
    def __init__(self, file_path: str, output_path: str, pdf_name: str) -> None:
        self.output_path = output_path
        self.pdf_name = pdf_name + ".pdf"
        self.pdf_filepath = self.output_path + self.pdf_name
        self.file_path = file_path

    @exception_handler
    def get_data(self, path: str) -> pd.DataFrame:
        return pd.read_excel(path)

    @exception_handler
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        new_df = df
        return new_df

    @exception_handler
    def df_to_html(self, df: pd.DataFrame) -> str:
        table = df.to_html(classes='mystyle')
        return f'''
        <html>
        <head><title>HTML Pandas Dataframe with CSS</title></head>
        <link rel="stylesheet" type="text/css" href="df_style.css"/>
        <body>
            {table}
        </body>
        </html>
        '''

    @exception_handler
    def export_pdf(self, html_string: str) -> None:
        HTML(string=html_string).write_pdf(self.pdf_filepath, stylesheets=["df_style.css"])

    @exception_handler
    def execute(self) -> None:
        df = self.get_data(self.file_path)

        new_df = self.transform_data(df)

        html_string = self.df_to_html(new_df)

        self.export_pdf(html_string)
